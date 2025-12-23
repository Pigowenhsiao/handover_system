# Change: Add attendance overtime block

## Why
Operators need to record overtime support details (category, count, notes) on each daily report.

## What Changes
- Add an overtime input block to the attendance page (category, count, notes).
- Persist a single overtime record per daily report in SQLite.
- Add i18n keys for overtime labels and category options.

## Impact
- Affected specs: attendance (new delta)
- Affected code: models.py, frontend/src/components/attendance_section_optimized.py, frontend/src/components/modern_main_frame.py, frontend/public/locales/*.json
