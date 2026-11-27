"""Playlist data and operations independent of the console and files."""

import random
import unicodedata
from dataclasses import dataclass, field


def clean_text(value: object, field_name: str) -> str:
    """Validate a required single-line field and trim surrounding whitespace."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be nonblank text.")
    if any(unicodedata.category(char) in {"Cc", "Cs", "Zl", "Zp"} for char in value):
        raise ValueError(f"{field_name} must fit on one line without control characters.")
    return value.strip()


def normalise(value: str) -> str:
    """Ignore case and repeated whitespace when comparing names."""
    return " ".join(value.split()).casefold()


@dataclass
class Song:
    """A song occurrence with a title, singer and genre."""

    name: str
    singer: str
    genre: str

    def __post_init__(self) -> None:
        """Validate all fields before a song can enter a playlist."""
        self.name = clean_text(self.name, "Song name")
        self.singer = clean_text(self.singer, "Singer")
        self.genre = clean_text(self.genre, "Genre")

    def __str__(self) -> str:
        """Format song details consistently for the screen and text export."""
        return f"{self.name} by {self.singer} [{self.genre}]"


@dataclass
class Playlist:
    """A named, ordered collection that can contain repeated songs."""

    name: str
    songs: list[Song] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the playlist name at creation."""
        self.name = clean_text(self.name, "Playlist name")

    def add_song(self, song: Song) -> None:
        """Append a song and preserve any existing occurrences of it."""
        self.songs.append(song)

    def edit_song(self, index: int, song: Song) -> None:
        """Replace the song at the selected zero-based position."""
        self.songs[index] = song

    def remove_song(self, index: int) -> Song:
        """Remove and return the song at the selected zero-based position."""
        return self.songs.pop(index)


class Library:
    """Manage playlist names, ordering and duplicate searches for one session."""

    def __init__(self) -> None:
        """Start a session with an empty library."""
        self.playlists: list[Playlist] = []

    def add_playlists(self, playlists: list[Playlist]) -> None:
        """Add the entire batch only after checking every name for collisions."""
        names = {normalise(playlist.name) for playlist in self.playlists}
        for playlist in playlists:
            key = normalise(playlist.name)
            if key in names:
                raise ValueError(f'A playlist named "{playlist.name}" already exists.')
            names.add(key)
        self.playlists.extend(playlists)

    def find_playlist(self, name: str) -> Playlist | None:
        """Find a playlist by normalised name, returning None if it is absent."""
        key = normalise(name)
        for playlist in self.playlists:
            if normalise(playlist.name) == key:
                return playlist
        return None

    def rename_playlist(self, playlist: Playlist, name: str) -> None:
        """Rename a playlist after checking that the new name is available."""
        name = clean_text(name, "Playlist name")
        key = normalise(name)
        if any(other is not playlist and normalise(other.name) == key for other in self.playlists):
            raise ValueError(f'A playlist named "{name}" already exists.')
        playlist.name = name

    def remove_playlist(self, playlist: Playlist) -> None:
        """Remove the selected playlist and all its entries from the library."""
        self.playlists.remove(playlist)

    def find_duplicates(
        self, playlists: list[Playlist] | None = None,
    ) -> list[tuple[Song, dict[str, int]]]:
        """Report matching titles and singers with occurrence counts per playlist."""
        selected = self.playlists if playlists is None else playlists
        matches: dict[tuple[str, str], tuple[Song, dict[str, int]]] = {}
        for playlist in selected:
            for song in playlist.songs:
                # Genre describes an occurrence and is excluded from song identity.
                key = (normalise(song.name), normalise(song.singer))
                _, counts = matches.setdefault(key, (song, {}))
                counts[playlist.name] = counts.get(playlist.name, 0) + 1
        return [(song, counts) for song, counts in matches.values() if sum(counts.values()) > 1]

    def sort_playlists(self) -> None:
        """Sort playlists by normalised name in ascending order."""
        self.playlists.sort(key=lambda playlist: normalise(playlist.name))

    def sort_songs(self) -> None:
        """Sort every playlist's songs by name and keep equal keys in input order."""
        for playlist in self.playlists:
            playlist.songs.sort(key=lambda song: normalise(song.name))

    def shuffle_songs(self, rng: random.Random | None = None) -> None:
        """Shuffle each playlist independently, using an optional test generator."""
        shuffle = random.shuffle if rng is None else rng.shuffle
        for playlist in self.playlists:
            shuffle(playlist.songs)
