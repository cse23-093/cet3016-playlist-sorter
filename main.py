"""Run the playlist sorter in a terminal."""

from getpass import getpass
from pathlib import Path

from library import Library, Playlist, Song
from playlist_files import read_playlists, write_export


DEMO_USERNAME = "user123"
DEMO_PASSWORD = "Givemetheykey123"
MAX_ATTEMPTS = 3


def authenticate() -> bool:
    """Grant entry only for the prescribed demo credentials within three tries."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        username = input("Username: ")
        password = getpass("Password: ")
        if username == DEMO_USERNAME and password == DEMO_PASSWORD:
            print("Login successful.")
            return True
        print("Incorrect username or password.")
        if attempt < MAX_ATTEMPTS:
            print(f"Attempts left: {MAX_ATTEMPTS - attempt}")
    print("Account locked for five minutes.")
    return False


def read_path(prompt: str) -> Path:
    """Read a nonblank path, allowing the quotes from Windows Copy as path."""
    value = input(prompt).strip().removeprefix('"').removesuffix('"')
    if not value:
        raise ValueError("Enter a file path.")
    return Path(value).absolute()


def import_playlists(library: Library) -> None:
    """Import all playlists from the selected file as a single batch."""
    path = read_path("JSON file path: ")
    playlists = read_playlists(path)
    library.add_playlists(playlists)
    print(f"Imported {len(playlists)} playlist(s).")


def view_library(library: Library) -> None:
    """Show the current playlists and songs in their stored order."""
    if not library.playlists:
        print("The library is empty.")
        return
    for number, playlist in enumerate(library.playlists, start=1):
        print(f"{number}. {playlist.name}")
        if not playlist.songs:
            print("   (empty playlist)")
        for position, song in enumerate(playlist.songs, start=1):
            print(f"   {position}. {song}")


def create_playlist(library: Library) -> None:
    """Create an empty playlist so the library can also be populated by hand."""
    playlist = Playlist(input("New playlist name: "))
    library.add_playlists([playlist])
    print(f'Created "{playlist.name}".')


def show_playlist_choices(library: Library) -> None:
    """List available playlists and stop the current action if the library is empty."""
    if not library.playlists:
        raise ValueError("The library is empty. Import or create a playlist first.")
    for number, playlist in enumerate(library.playlists, start=1):
        print(f"{number}. {playlist.name} ({len(playlist.songs)} song(s))")


def selection_index(value: str, count: int) -> int:
    """Turn a valid displayed number into a zero-based list index."""
    value = value.strip()
    if not value.isascii() or not value.isdecimal():
        raise ValueError("Enter one of the displayed numbers.")
    index = int(value) - 1
    if not 0 <= index < count:
        raise ValueError("Selection is out of range.")
    return index


def select_playlist(library: Library) -> Playlist:
    """Select by name first, then by displayed number if no name matches."""
    show_playlist_choices(library)
    choice = input("Playlist name or number: ").strip()
    playlist = library.find_playlist(choice)
    if playlist is not None:
        return playlist
    if choice.isascii() and choice.isdecimal():
        return library.playlists[selection_index(choice, len(library.playlists))]
    raise ValueError("Enter the name or number of a displayed playlist.")


def select_song(playlist: Playlist) -> int:
    """Select one exact occurrence from a numbered list of songs."""
    if not playlist.songs:
        raise ValueError(f'"{playlist.name}" has no songs.')
    for position, song in enumerate(playlist.songs, start=1):
        print(f"{position}. {song}")
    return selection_index(input("Song number: "), len(playlist.songs))


def read_song(current: Song | None = None) -> Song:
    """Read a complete song, keeping a field when Enter is pressed during editing."""
    if current is None:
        return Song(input("Song name: "), input("Singer: "), input("Genre: "))
    return Song(
        input(f"Song name [{current.name}]: ") or current.name,
        input(f"Singer [{current.singer}]: ") or current.singer,
        input(f"Genre [{current.genre}]: ") or current.genre,
    )


def add_song(library: Library) -> None:
    """Add a song to an existing playlist."""
    playlist = select_playlist(library)
    song = read_song()
    playlist.add_song(song)
    print(f'Added {song} to "{playlist.name}".')


def edit_song(library: Library) -> None:
    """Update one selected song after validating all proposed fields."""
    playlist = select_playlist(library)
    index = select_song(playlist)
    playlist.edit_song(index, read_song(playlist.songs[index]))
    print(f"Updated {playlist.songs[index]}.")


def rename_playlist(library: Library) -> None:
    """Prompt for a new name and leave the playlist's songs in place."""
    playlist = select_playlist(library)
    library.rename_playlist(playlist, input("New playlist name: "))
    print(f'Renamed playlist to "{playlist.name}".')


def confirm(prompt: str) -> bool:
    """Return true only when the user explicitly confirms an action."""
    return input(f"{prompt} [y/N] ").strip().casefold() in {"y", "yes"}


def remove_playlist(library: Library) -> None:
    """Confirm deletion of the selected playlist and its songs."""
    playlist = select_playlist(library)
    if confirm(f'Delete "{playlist.name}" and its {len(playlist.songs)} song(s)?'):
        library.remove_playlist(playlist)
        print(f'Deleted "{playlist.name}".')
    else:
        print("Deletion cancelled.")


def remove_song(library: Library) -> None:
    """Confirm deletion of one song occurrence from its playlist."""
    playlist = select_playlist(library)
    index = select_song(playlist)
    if confirm(f'Delete {playlist.songs[index]} from "{playlist.name}"?'):
        print(f"Deleted {playlist.remove_song(index)}.")
    else:
        print("Deletion cancelled.")


def find_duplicates(library: Library) -> None:
    """Show duplicate counts in one, several or all playlists."""
    show_playlist_choices(library)
    choice = input('Playlist numbers separated by commas, or "all": ').strip()
    playlists = library.playlists
    if choice.casefold() != "all":
        indices = dict.fromkeys(selection_index(part, len(playlists)) for part in choice.split(","))
        playlists = [playlists[index] for index in indices]

    matches = library.find_duplicates(playlists)
    if not matches:
        print("No duplicate songs found.")
    for song, counts in matches:
        locations = ", ".join(f"{name} ({count})" for name, count in counts.items())
        print(f"{song.name} by {song.singer} -> {locations}")


def sort_playlists(library: Library) -> None:
    """Sort playlists by name and acknowledge the operation."""
    library.sort_playlists()
    print("Playlists sorted by name.")


def sort_songs(library: Library) -> None:
    """Sort songs by name within each playlist."""
    library.sort_songs()
    print("Songs sorted by name within each playlist.")


def shuffle_songs(library: Library) -> None:
    """Shuffle songs within each playlist."""
    library.shuffle_songs()
    print("Songs shuffled within each playlist.")


def export_library(library: Library) -> None:
    """Export the current library, asking permission to replace an existing file."""
    path = read_path("Export .txt path: ")
    try:
        write_export(path, library)
    except FileExistsError:
        if not confirm(f'Overwrite "{path}"?'):
            print("Export cancelled.")
            return
        write_export(path, library, overwrite=True)
    print(f"Exported to {path}")


def run_menu(library: Library) -> None:
    """Dispatch menu actions and report invalid selections or failed operations."""
    actions = {
        "1": ("Import playlists", import_playlists),
        "2": ("View library", view_library),
        "3": ("Create playlist", create_playlist),
        "4": ("Add song", add_song),
        "5": ("Edit song", edit_song),
        "6": ("Rename playlist", rename_playlist),
        "7": ("Delete playlist", remove_playlist),
        "8": ("Delete song", remove_song),
        "9": ("Find duplicates", find_duplicates),
        "10": ("Sort playlists by name", sort_playlists),
        "11": ("Sort songs by name", sort_songs),
        "12": ("Shuffle songs", shuffle_songs),
        "13": ("Export to text", export_library),
    }
    while True:
        print("\nPlaylist sorter")
        for number, (label, _) in actions.items():
            print(f"{number}. {label}")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye.")
            return
        if choice not in actions:
            print("Choose a number from the menu.")
            continue
        _, action = actions[choice]
        try:
            action(library)
        except (OSError, ValueError) as error:
            print(f"Error: {error}")


def main() -> int:
    """Authenticate before creating the library and handle terminal interruptions."""
    try:
        if not authenticate():
            return 1
        run_menu(Library())
    except (EOFError, KeyboardInterrupt):
        print("\nSession ended.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
