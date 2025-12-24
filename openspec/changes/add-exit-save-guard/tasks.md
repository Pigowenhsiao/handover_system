## 1. Implementation
- [x] 1.1 Add close handler in ModernMainFrame to flush edits and attempt saves.
- [x] 1.2 Block exit when pending import records exist or when a save fails.
- [x] 1.3 Force restart after database path changes via the close handler.
- [x] 1.4 Wire WM_DELETE_WINDOW to the ModernMainFrame close handler.
- [x] 1.5 Add manual verification notes.

## Manual Verification
- Change the database path, confirm the app saves, then closes and requires restart.
- Select a non-existent database path and confirm the app prompts to copy or create a blank database.
- Attempt to exit with pending import rows and confirm a force-exit prompt appears.
- Simulate a save failure and confirm a force-exit prompt appears.
- Modify attendance data, close the app, and confirm the data persists after restart.
