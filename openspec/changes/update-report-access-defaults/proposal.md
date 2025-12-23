# Change: Update report access and defaults

## Why
Unauthenticated users can access report pages, and daily report filters are pre-selected instead of requiring explicit user choice.

## What Changes
- Require login before opening attendance summary, summary query, and abnormal history pages.
- Allow those report pages without forcing daily report basic info to be saved.
- Leave shift and area blank on daily report creation to force explicit selection.

## Impact
- Affected specs: report-access (new)
- Affected code: frontend/src/components/modern_main_frame.py
