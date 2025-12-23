## Context
Attendance currently stores regular and contract staffing counts and reasons per report.
We need a single overtime record per report with category, count, and notes.

## Goals / Non-Goals
- Goals: capture overtime category/count/notes per report; persist and restore in UI.
- Non-Goals: show overtime in summary reports or exports; support multiple overtime rows.

## Decisions
- Use a new table `overtime_entries` with `report_id`, `category`, `count`, `notes`.
- Enforce single record per report by deleting existing row and inserting the new one on save.
- Keep category optional (blank default); only persist when any field is provided.

## Risks / Trade-offs
- Adding a new table requires a schema update on existing databases.
  Mitigation: rely on SQLAlchemy create_all to add the table without altering existing data.

## Migration Plan
1. Deploy code that defines the new model.
2. On startup, `create_all` creates the `overtime_entries` table if missing.
3. No data backfill required.

## Open Questions
- None.
