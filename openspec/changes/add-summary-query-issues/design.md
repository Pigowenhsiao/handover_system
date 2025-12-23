## Context
Summary Query currently shows daily report summary fields only.
Equipment and lot issues are visible in a separate Abnormal History page.

## Goals / Non-Goals
- Goals: show full equipment and lot issue details inside Summary Query results.
- Non-Goals: remove Abnormal History; change storage schema.

## Decisions
- Expand Summary Query columns to include all equipment/lot fields.
- Build one row per equipment log and one row per lot log.
- Repeat the summary fields (date/shift/area/key output/issues/countermeasures) per row.
- Leave unrelated columns empty (e.g., lot columns blank on equipment rows).

## Risks / Trade-offs
- Larger result sets due to row expansion.
  Mitigation: keep existing date/shift/area filters and ordering.

## Migration Plan
No schema changes required.

## Open Questions
- None.
