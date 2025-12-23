# Change: Guard data persistence on exit

## Why
Users can lose in-progress edits if the application closes before data is written to SQLite.

## What Changes
- Add an application close handler that flushes inline edits and attempts to save daily report and attendance data before exit.
- Block exit when there are pending import records that have not been uploaded.
- Force a restart after database path changes, after persisting any in-flight data.

## Impact
- Affected specs: data-persistence (new)
- Affected code: handover_system.py, frontend/src/components/modern_main_frame.py
