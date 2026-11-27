# Ten-minute demonstration

Run `python -B main.py` in a terminal from the project folder. Keep `main.py`, `library.py` and `playlist_files.py` open in your editor. Use a fresh `.txt` name for each rehearsal so the first export needs no overwrite prompt.

| Time | Actions and evidence |
| --- | --- |
| 0:00–1:00 | Enter the wrong credentials three times. Show the five-minute lockout message and exit. Start a fresh process, log in with the demo credentials from the README and show the numbered menu. |
| 1:00–2:00 | Choose `1` and import `examples/demo.json`. Choose `2` to show the three playlists and the empty `Desk Mix`. Use `1` again with `examples/invalid.json`, then `2` to show that the first record from that file was also rejected. |
| 2:00–3:00 | Choose `9` and enter `1` to find two copies of `Blue Hour` by Léa Moss in `Road Trip`. Repeat with `all` to show `Road Trip (2)` and `After Dark (1)`. Point out the similarly titled song by Kai Grey. Show the dictionary grouping in `Library.find_duplicates`. |
| 3:00–5:30 | Use `3` to create `Rehearsal Mix`. Use `4` to add `Warm Up` by `Mina Vale` in `Soul`. Use `5`, select song `1`, press Enter to retain the title and singer, and enter `Jazz` for the genre. Use `6` to rename `Rehearsal Mix` to `Studio Mix`. Use `8`, enter `Road Trip`, select song `3` and confirm with `y`. Use `7` to delete `Studio Mix` and confirm with `y`. Choose `2` to show the result. |
| 5:30–7:00 | Use `10` and `11`, then `2` to show playlist order and song order. Use `12` and `2` again to show that the song order can change while the playlists stay in place. Shuffle can return the same order. If that happens, say so and try once more. |
| 7:00–8:00 | Choose `13` and enter `demo-export.txt` or a fresh `.txt` name. Open the resulting file, then show its playlist lines, song details and empty playlist marker. Return to the app and use `0` to exit. |
| 8:00–9:00 | Run `python -B -m unittest discover -s tests`. Show a source example, such as the validation before `Library.add_playlists` commits the import, and the corresponding failed-import check in `test_all_menu_actions_in_a_single_session`. |
| 9:00–10:00 | Give your own evaluation. Use one test result to support a strength, explain a limitation that was visible during the demo, and say what usage would justify the next change. |

## Reflection prompts

- **Import reliability.** Why does the rejected import leave the valid first playlist out too? How does that help when a user corrects the file and tries again?
- **Session storage.** What happens to an edit after restarting? Local JSON saving could support one person resuming a session. A database becomes worth evaluating when several people need to edit concurrently or when measured loading and search costs exceed what an in-memory library can handle.
- **Duplicate identity.** Could a studio and live recording share a title and singer? How would track IDs change the result if the import source provided them?
- **Authentication.** What does the failed-login test prove? What changes would a shared deployment need so that restarting the app does not reset the lockout?
