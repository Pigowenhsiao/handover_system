# Change: Enable editing attendance summary report

## Why
Attendance summary entries can be saved with incorrect date/shift/area and need correction.

## What Changes
- Allow editing attendance summary rows (date/shift/area) via double-click.
- Add an Update action that saves changes and records the latest modifier and timestamp.
- Display the latest modifier info as the last column in the attendance summary table.

## Impact
- Affected specs: attendance (new delta)
- Affected code: models.py, frontend/src/components/modern_main_frame.py, frontend/public/locales/*.json
