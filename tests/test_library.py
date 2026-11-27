"""Verify playlist rules independently of console input and file paths."""

from collections import Counter
from random import Random
from unittest import TestCase
from unittest.mock import Mock

from library import Library, Playlist, Song


class LibraryTests(TestCase):
    """Exercise in-memory validation, edits and ordering."""

    def test_song_requires_single_line_text_fields(self) -> None:
        """Keep Unicode and punctuation while rejecting invalid data."""
        self.assertEqual(Song("  Léa's Song  ", "  Léa ", " Jazz "), Song("Léa's Song", "Léa", "Jazz"))
        for fields in [("", "Singer", "Jazz"), ("Title", None, "Jazz"), ("Title", "Singer", " "),
                       ("Title\nSecond line", "Singer", "Jazz"), ("Title", "Singer\x1b", "Jazz")]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                Song(*fields)

    def test_add_edit_and_remove_exact_occurrences(self) -> None:
        """Preserve the unselected copies when editing and removing songs."""
        original = Song("Same Title", "Mina", "Jazz")
        changed = Song("Changed Title", "Mina", "Soul")
        first, second = Playlist("First"), Playlist("Second", [original])
        first.add_song(original)
        first.add_song(original)
        first.edit_song(1, changed)
        self.assertEqual(first.songs, [original, changed])
        self.assertEqual(first.remove_song(0), original)
        self.assertEqual(first.remove_song(0), changed)
        self.assertEqual(first.songs, [])
        self.assertEqual(second.songs, [original])

    def test_playlist_batch_rejects_existing_and_internal_collisions(self) -> None:
        """Keep the prior library intact even when a later name conflicts."""
        library = Library()
        original = Playlist("Road Trip")
        library.add_playlists([original])
        for batch in ([Playlist("New"), Playlist(" road   trip ")], [Playlist("New"), Playlist("NEW")]):
            with self.subTest(batch=batch), self.assertRaises(ValueError):
                library.add_playlists(batch)
            self.assertEqual(library.playlists, [original])

    def test_rename_checks_collisions_and_preserves_order_and_songs(self) -> None:
        """Allow changing the spelling of an existing name without moving it."""
        library = Library()
        song = Song("Amber", "Mina", "Jazz")
        first, second = Playlist("Road Trip", [song]), Playlist("After Dark")
        library.add_playlists([first, second])
        for invalid in (" ", "after   DARK"):
            with self.subTest(name=invalid), self.assertRaises(ValueError):
                library.rename_playlist(first, invalid)
            self.assertEqual(first.name, "Road Trip")
        library.rename_playlist(first, " ROAD TRIP ")
        self.assertIs(library.find_playlist("road   trip"), first)
        self.assertIsNone(library.find_playlist("Missing"))
        self.assertEqual(first.name, "ROAD TRIP")
        self.assertEqual(first.songs, [song])
        self.assertEqual(library.playlists, [first, second])

    def test_remove_playlist_preserves_another_playlist_with_same_song(self) -> None:
        """Restrict playlist deletion to the selected collection."""
        library = Library()
        song = Song("Amber", "Mina", "Jazz")
        first, second = Playlist("First", [song]), Playlist("Second", [song])
        library.add_playlists([first, second])
        library.remove_playlist(first)
        self.assertEqual(library.playlists, [second])
        self.assertEqual(second.songs, [song])

    def test_duplicate_counts_cover_one_several_and_all_playlists(self) -> None:
        """Group case and whitespace variants across genres while keeping different singers distinct."""
        library = Library()
        original = Song("Blue Hour", "Léa", "Jazz")
        same = Song("blue  HOUR", "LÉA", "Soul")
        different = Song("Blue Hour", "Kai", "Jazz")
        first = Playlist("First", [original, same])
        second = Playlist("Second", [original, different])
        third = Playlist("Third", [same])
        library.add_playlists([first, second, third])

        self.assertEqual(library.find_duplicates([first]), [(original, {"First": 2})])
        self.assertEqual(library.find_duplicates([second, third]), [(original, {"Second": 1, "Third": 1})])
        self.assertEqual(library.find_duplicates(), [(original, {"First": 2, "Second": 1, "Third": 1})])
        self.assertEqual(library.find_duplicates([second]), [])
        self.assertEqual(first.songs, [original, same])
        self.assertEqual(second.songs, [original, different])

    def test_sorts_are_case_insensitive_and_song_ties_are_stable(self) -> None:
        """Sort independently and preserve metadata and tied song order."""
        library = Library()
        zebra = Song("Zebra", "Mina", "Pop")
        lower = Song("amber", "Kai", "Jazz")
        upper = Song("Amber", "Léa", "Soul")
        last = Playlist("zoo", [zebra, lower, upper])
        empty = Playlist("Alpha")
        single = Playlist("beta", [zebra])
        library.add_playlists([last, empty, single])

        library.sort_songs()
        self.assertEqual(library.playlists, [last, empty, single])
        self.assertEqual(last.songs, [lower, upper, zebra])
        library.sort_playlists()
        library.sort_songs()
        library.sort_playlists()
        self.assertEqual(library.playlists, [empty, single, last])
        self.assertEqual(empty.songs, [])
        self.assertEqual(single.songs, [zebra])
        self.assertEqual(last.songs, [lower, upper, zebra])

    def test_shuffle_preserves_every_occurrence_and_playlist_order(self) -> None:
        """Verify membership and metadata without relying on a chance change in order."""
        library = Library()
        song = Song("Amber", "Kai", "Jazz")
        other = Song("Zebra", "Mina", "Soul")
        playlists = [Playlist("First", [song, song, other]), Playlist("Two", [other, song]), Playlist("Empty")]
        library.add_playlists(playlists)
        before = [Counter(map(str, playlist.songs)) for playlist in playlists]
        rng = Mock(spec=Random)
        rng.shuffle.side_effect = list.reverse

        library.shuffle_songs(rng)

        self.assertEqual(rng.shuffle.call_count, 3)
        self.assertEqual(library.playlists, playlists)
        self.assertEqual([playlist.songs for playlist in playlists], [[other, song, song], [song, other], []])
        self.assertEqual([Counter(map(str, playlist.songs)) for playlist in playlists], before)

    def test_empty_library_supports_ordering_and_duplicate_checks(self) -> None:
        """Treat an empty session as a valid library."""
        library = Library()
        library.sort_playlists()
        library.sort_songs()
        library.shuffle_songs()
        self.assertEqual(library.find_duplicates(), [])
        self.assertEqual(library.playlists, [])
