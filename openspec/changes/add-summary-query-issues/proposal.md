# Change: Add equipment and lot issues to summary query

## Why
Users need to see equipment and lot issue details directly in the Summary Query report without relying on Abnormal History.

## What Changes
- Expand Summary Query results to include all equipment and lot issue fields.
- Render multiple rows per report when there are multiple equipment/lot records.
- Keep existing summary fields in each row for context.

## Impact
- Affected specs: summary-query (new delta)
- Affected code: frontend/src/components/modern_main_frame.py, frontend/public/locales/*.json
