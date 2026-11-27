"""Read local JSON playlists and write human-readable text exports."""

import json
from pathlib import Path

from library import Library, Playlist, Song


def read_playlists(path: Path) -> list[Playlist]:
    """Read and validate all playlist and song records before returning them."""
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("playlists"), list):
        raise ValueError('The file must contain a top-level "playlists" list.')

    playlists = []
    for number, record in enumerate(data["playlists"], start=1):
        if not isinstance(record, dict) or not isinstance(record.get("songs"), list):
            raise ValueError(f'Playlist {number} must be an object with a "songs" list.')
        try:
            playlist = Playlist(record["name"])
        except (KeyError, ValueError) as error:
            raise ValueError(f"Playlist {number} needs a valid name.") from error

        for position, details in enumerate(record["songs"], start=1):
            if not isinstance(details, dict):
                raise ValueError(f'Playlist "{playlist.name}", song {position} must be an object.')
            try:
                song = Song(details["name"], details["singer"], details["genre"])
            except KeyError as error:
                raise ValueError(
                    f'Playlist "{playlist.name}", song {position} is missing {error}.',
                ) from error
            except ValueError as error:
                raise ValueError(f'Playlist "{playlist.name}", song {position}. {error}') from error
            playlist.add_song(song)
        playlists.append(playlist)
    return playlists


def write_export(path: Path, library: Library, *, overwrite: bool = False) -> None:
    """Write one line per playlist in current order and protect existing files by default."""
    if path.suffix.casefold() != ".txt":
        raise ValueError("The export path must end in .txt.")

    lines = []
    for playlist in library.playlists:
        songs = " | ".join(str(song) for song in playlist.songs) or "(empty playlist)"
        lines.append(f"{playlist.name} -> {songs}\n")
    with path.open("w" if overwrite else "x", encoding="utf-8") as export:
        export.writelines(lines)
