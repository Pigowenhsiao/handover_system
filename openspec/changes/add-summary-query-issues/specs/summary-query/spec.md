## ADDED Requirements
### Requirement: Summary Query shows equipment and lot issues
The system SHALL display all equipment and lot issue fields in the Summary Query report and expand results into multiple rows when multiple records exist.

#### Scenario: Equipment issues expanded
- **WHEN** a daily report has multiple equipment logs
- **THEN** Summary Query shows one row per equipment log with all equipment fields populated and lot fields blank

#### Scenario: Lot issues expanded
- **WHEN** a daily report has multiple lot logs
- **THEN** Summary Query shows one row per lot log with all lot fields populated and equipment fields blank

#### Scenario: Mixed issues
- **WHEN** a daily report has both equipment and lot logs
- **THEN** Summary Query includes rows for each log with the summary fields repeated
