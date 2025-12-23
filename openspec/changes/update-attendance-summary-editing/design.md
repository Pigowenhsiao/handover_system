## Context
The attendance summary table shows daily report entries but is currently read-only.
Users need to correct mistaken date/shift/area values and track the last modification.

## Goals / Non-Goals
- Goals: edit date/shift/area for an existing report; store and display latest modifier and time.
- Non-Goals: editing attendance counts or summary statistics; multi-step audit history.

## Decisions
- Add `last_modified_by` (string) and `last_modified_at` (datetime) to `DailyReport`.
- On update, set these fields to the current logged-in user and current timestamp.
- Show a single "last modified" column in the summary table (username + formatted time).

## Risks / Trade-offs
- Updating date/shift/area changes the unique key for a report; conflicts must be handled.
  Mitigation: validate uniqueness before saving and show a warning on conflict.

## Migration Plan
1. Deploy code with new model fields.
2. SQLAlchemy `create_all` adds columns on existing databases.
3. Existing rows show empty last-modified until edited.

## Open Questions
- None.
