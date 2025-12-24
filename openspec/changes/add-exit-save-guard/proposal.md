# Change: Guard data persistence on exit

## Why
Users can lose in-progress edits if the application closes before data is written to SQLite.

## What Changes
- Add an application close handler that flushes inline edits and attempts to save daily report and attendance data before exit.
- Prompt for forced exit when there are pending import records or data persistence fails.
- Force a restart after database path changes, after attempting to persist in-flight data (and prompt for forced exit on failure).

## Impact
- Affected specs: data-persistence (new)
- Affected code: handover_system.py, frontend/src/components/modern_main_frame.py
