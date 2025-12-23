## ADDED Requirements
### Requirement: Persist data on application exit
The system SHALL flush in-progress edits and attempt to save report and attendance data before closing the application.

#### Scenario: Inline edit is flushed
- **WHEN** a user closes the application while an inline table edit is active
- **THEN** the edit is committed before exit proceeds

#### Scenario: Attendance changes are saved
- **WHEN** a user closes the application with modified attendance data
- **THEN** the system saves the attendance changes before exit proceeds

#### Scenario: Daily report summary is saved
- **WHEN** a user closes the application with daily report content entered
- **THEN** the system saves the daily report summary before exit proceeds

#### Scenario: Pending imports block exit
- **WHEN** there are pending import records that have not been uploaded
- **THEN** the application blocks exit until the data is saved or cleared

#### Scenario: Database path change forces restart
- **WHEN** a user updates the database path
- **THEN** the system saves in-flight data, informs the user, and closes the application to require a restart
