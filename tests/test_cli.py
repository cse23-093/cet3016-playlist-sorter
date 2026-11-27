"""Exercise the application's normal entry point with scripted terminal input."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import main


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ConsoleTests(TestCase):
    """Cover authentication, navigation, confirmation and integrated actions."""

    def run_session(
        self, answers: list[str], passwords: tuple[str, ...] = ("Givemetheykey123",),
    ) -> tuple[int, str]:
        """Run the real application with scripted responses and capture its output."""
        output = StringIO()
        with (patch("builtins.input", side_effect=answers),
              patch("main.getpass", side_effect=passwords), redirect_stdout(output)):
            status = main.main()
        return status, output.getvalue()

    def test_exact_credentials_succeed_after_two_failures(self) -> None:
        """Check case sensitivity and preserve whitespace in password comparisons."""
        status, output = self.run_session(
            ["user123", "USER123", "user123", "0"],
            ("Givemetheykey123 ", "Givemetheykey123", "Givemetheykey123"),
        )
        self.assertEqual(status, 0)
        self.assertEqual(output.count("Incorrect username or password."), 2)
        self.assertIn("Attempts left: 2", output)
        self.assertIn("Attempts left: 1", output)
        self.assertIn("Login successful.", output)
        self.assertNotIn("locked", output)

    def test_three_failures_include_blank_input_and_do_not_show_menu(self) -> None:
        """End authentication at the third failure before any actions are shown."""
        status, output = self.run_session(["wrong", "", "user123"], ("wrong", "", "wrong"))
        self.assertEqual(status, 1)
        self.assertEqual(output.count("Incorrect username or password."), 3)
        self.assertIn("Account locked for five minutes.", output)
        self.assertNotIn("Playlist sorter", output)

    def test_terminal_interrupts_end_the_session_cleanly(self) -> None:
        """Handle both Ctrl+C and end of input without a traceback."""
        for error in (EOFError, KeyboardInterrupt):
            output = StringIO()
            with (self.subTest(error=error), patch("builtins.input", side_effect=error), redirect_stdout(output)):
                self.assertEqual(main.main(), 0)
            self.assertIn("Session ended.", output.getvalue())

    def test_all_menu_actions_in_a_single_session(self) -> None:
        """Run the full workflow from login through import, changes and text export."""
        with TemporaryDirectory() as directory:
            export = Path(directory) / "set list.txt"
            status, output = self.run_session([
                "user123", "wrong option",
                "1", f'"{EXAMPLES / "demo.json"}"',
                "1", str(EXAMPLES / "invalid.json"),
                "2",
                "9", "1", "9", "2,1", "9", "2,2", "9", "all",
                "3", "Practice",
                "4", "practice", "Zebra", "Mina", "Pop",
                "5", "Practice", "1", "  ", "", "",
                "2",
                "5", "Practice", "1", "Amber", "", "Soul",
                "6", "4", "Session Notes",
                "7", "Session Notes", "n",
                "8", "Session Notes", "1", "n",
                "8", "Road Trip", "99",
                "8", "Road Trip", "3", "y",
                "7", "Road Trip", "y",
                "10", "11", "2", "12",
                "13", str(export),
                "0",
            ])
            lines = export.read_text(encoding="utf-8").splitlines()

        self.assertEqual(status, 0)
        for message in [
            "Choose a number from the menu.", "Imported 3 playlist(s).", "is missing 'genre'",
            "Blue Hour by Léa Moss -> Road Trip (2)", "After Dark (1), Road Trip (2)",
            "Road Trip (2), After Dark (1)", "No duplicate songs found.", 'Created "Practice".',
            'Added Zebra by Mina [Pop] to "Practice".', "Song name must be nonblank text.",
            "1. Zebra by Mina [Pop]", "Updated Amber by Mina [Soul].", 'Renamed playlist to "Session Notes".',
            "Selection is out of range.", "Deleted Blue Hour by Léa Moss [Acoustic].", 'Deleted "Road Trip".',
            "Playlists sorted by name.", "Songs sorted by name within each playlist.",
            "Songs shuffled within each playlist.", f"Exported to {export}", "Goodbye.",
        ]:
            with self.subTest(message=message):
                self.assertIn(message, output)
        self.assertEqual(output.count("Deletion cancelled."), 2)
        self.assertNotIn("Valid First Playlist", output)
        self.assertEqual([line.split(" -> ")[0] for line in lines], ["After Dark", "Desk Mix", "Session Notes"])
        self.assertEqual(lines[-1], "Session Notes -> Amber by Mina [Soul]")

    def test_overwrite_can_be_cancelled_or_confirmed(self) -> None:
        """Keep a previous file on cancellation and replace it on confirmation."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "export.txt"
            path.write_text("Previous export", encoding="utf-8")
            prefix = ["user123", "3", "Practice", "13", str(path)]
            _, output = self.run_session([*prefix, "n", "0"])
            self.assertIn("Export cancelled.", output)
            self.assertNotIn("Exported to", output)
            self.assertEqual(path.read_text(encoding="utf-8"), "Previous export")

            _, output = self.run_session([*prefix, "y", "0"])
            self.assertIn("Exported to", output)
            self.assertEqual(path.read_text(encoding="utf-8"), "Practice -> (empty playlist)\n")

    def test_invalid_paths_and_empty_selections_return_to_the_menu(self) -> None:
        """Report expected failures and keep the session available afterward."""
        with TemporaryDirectory() as directory:
            missing = Path(directory) / "missing" / "export.txt"
            status, output = self.run_session([
                "user123", "4", "1", " ", "13", str(missing), "13", "wrong.json",
                "3", "Empty", "9", "", "8", "Empty", "2", "0",
            ])
        self.assertEqual(status, 0)
        for message in ["library is empty", "Enter a file path.", "must end in .txt",
                        "Enter one of the displayed numbers.", '"Empty" has no songs.', "(empty playlist)"]:
            with self.subTest(message=message):
                self.assertIn(message, output)
        self.assertEqual(output.count("Error:"), 6)
        self.assertNotIn("Exported to", output)
