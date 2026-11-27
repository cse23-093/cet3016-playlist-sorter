# CET3016 Playlist Sorter

A single-user Python console app for importing, editing, sorting, shuffling and exporting music playlists. It uses the standard library and was verified with Python 3.12.10 on Windows.

## Run and test

Run the app from a terminal in this folder.

```powershell
python -B main.py
```

Use `user123` and `Givemetheykey123` to sign in. The password is case-sensitive. After three failed attempts, the app displays the five-minute lockout message and exits. The brief permits a message-only lockout, so starting the program again gives a fresh set of attempts.

```powershell
python -B -m unittest discover -s tests
```

All 21 automated tests passed with normal Windows permissions. They cover login, every menu action, invalid inputs and file errors. A separate Windows terminal walkthrough confirmed hidden password input, the three-attempt exit and the demo workflow through text export. 

## Files and playlist rules

- **Import.** Choose `1` and enter `examples/demo.json`. The input is a UTF-8 JSON object with a `playlists` list. Each playlist has `name` and `songs` fields. Each song has `name`, `singer` and `genre` fields. The app checks the complete file before adding any playlists. `examples/invalid.json` demonstrates rejection of a batch with a missing field.
- **Edit and search.** Choose a playlist by displayed name or number, then choose the exact song occurrence by number. Use Enter to keep an existing song field while editing. Duplicate search accepts one number, comma-separated numbers or `all`. A duplicate is a matching title and singer after folding case and normalising whitespace. The result identifies all affected playlists and their occurrence counts.
- **Order and export.** Both sorts compare names case-insensitively. Shuffle reorders only the songs within each playlist and may leave some orders unchanged. Choose `13` and enter a `.txt` path. The UTF-8 export contains one line per playlist in the current order. An existing export requires confirmation before replacement.
- **Session data.** Each run starts with an empty library. JSON is the input format and the text export is a readable record of the current session. Export before exiting if you want a record of your changes.


