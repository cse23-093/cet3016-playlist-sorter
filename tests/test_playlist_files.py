"""Verify file formats and file errors using isolated temporary paths."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from library import Library, Playlist, Song
from playlist_files import read_playlists, write_export


class PlaylistFileTests(TestCase):
    """Cover validated JSON imports and ordered UTF-8 exports."""

    def setUp(self) -> None:
        """Create a clean temporary directory for each test."""
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def test_import_preserves_order_unicode_empty_playlists_and_repeats(self) -> None:
        """Read a file with a UTF-8 BOM and multiple playlist records."""
        path = self.directory / "library.json"
        song = {"name": "Blue Hour", "singer": "Léa", "genre": "Jazz"}
        data = {"playlists": [{"name": "Road Trip", "songs": [song, song]}, {"name": "Desk", "songs": []}]}
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8-sig")
        self.assertEqual(
            read_playlists(path),
            [Playlist("Road Trip", [Song("Blue Hour", "Léa", "Jazz")] * 2), Playlist("Desk")],
        )

    def test_import_rejects_malformed_json(self) -> None:
        """Reject invalid JSON syntax instead of returning an incomplete list."""
        path = self.directory / "broken.json"
        path.write_text('{"playlists": [', encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            read_playlists(path)

    def test_import_rejects_wrong_shapes_missing_fields_and_invalid_types(self) -> None:
        """Validate the document, playlist and song levels."""
        path = self.directory / "wrong.json"
        invalid_data = [
            [], {"playlists": {}}, {"playlists": [None]}, {"playlists": [{"songs": []}]},
            {"playlists": [{"name": "Mix", "songs": ["a song"]}]},
            {"playlists": [{"name": "Mix", "songs": [{"name": "Amber", "singer": "Mina"}]}]},
            {"playlists": [{"name": "Mix", "songs": [{"name": 42, "singer": "Mina", "genre": "Jazz"}]}]},
        ]
        for data in invalid_data:
            with self.subTest(data=data):
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_playlists(path)

    def test_import_reports_missing_and_non_utf8_files(self) -> None:
        """Propagate file and decoding errors so the menu can report them."""
        path = self.directory / "missing.json"
        with self.assertRaises(FileNotFoundError):
            read_playlists(path)
        path.write_bytes(b"\xff")
        with self.assertRaises(UnicodeDecodeError):
            read_playlists(path)

    def test_export_writes_one_line_per_playlist_in_current_order(self) -> None:
        """Include song fields, Unicode and an explicit empty playlist marker."""
        library = Library()
        library.add_playlists([
            Playlist("Road Trip", [Song("Zebra", "Léa", "Jazz"), Song("Amber", "Kai", "Soul")]),
            Playlist("Desk"),
        ])
        path = self.directory / "output.txt"
        write_export(path, library)
        self.assertEqual(path.read_text(encoding="utf-8").splitlines(), [
            "Road Trip -> Zebra by Léa [Jazz] | Amber by Kai [Soul]",
            "Desk -> (empty playlist)",
        ])

    def test_export_refuses_existing_file_unless_overwrite_is_set(self) -> None:
        """Preserve an existing export until an overwrite is explicitly requested."""
        library = Library()
        library.add_playlists([Playlist("Empty")])
        path = self.directory / "output.txt"
        path.write_text("Previous export", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            write_export(path, library)
        self.assertEqual(path.read_text(encoding="utf-8"), "Previous export")
        write_export(path, library, overwrite=True)
        self.assertEqual(path.read_text(encoding="utf-8"), "Empty -> (empty playlist)\n")
