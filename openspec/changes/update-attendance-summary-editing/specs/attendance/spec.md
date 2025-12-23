## ADDED Requirements
### Requirement: Edit Attendance Summary Rows
The system SHALL allow editing the attendance summary report rows to correct date, shift, and area values via a double-click action and an explicit update action.

#### Scenario: Update summary row
- **WHEN** a user double-clicks a summary row and updates date/shift/area
- **THEN** the report is saved and the summary table reflects the changes

#### Scenario: Track last modification
- **WHEN** the user updates a summary row
- **THEN** the system records and displays the latest modifier and timestamp as the last column

#### Scenario: Prevent key conflicts
- **WHEN** the updated date/shift/area would conflict with an existing report
- **THEN** the system rejects the update and shows a warning
