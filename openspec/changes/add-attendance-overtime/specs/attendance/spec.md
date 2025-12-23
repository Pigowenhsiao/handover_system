## ADDED Requirements
### Requirement: Overtime Attendance Input
The system SHALL provide an overtime input block on the attendance page that captures category (Regular/Contract), count, and notes for a single overtime record per daily report, with a blank default category.

#### Scenario: Save overtime details
- **WHEN** the user selects a category and enters count/notes then saves attendance
- **THEN** the overtime record is stored with the current daily report and restored on load

#### Scenario: Clear overtime details
- **WHEN** the user leaves category blank and clears count/notes then saves attendance
- **THEN** any existing overtime record for that report is removed

#### Scenario: Language switching
- **WHEN** the user switches language
- **THEN** the overtime labels and category options update to the selected language
