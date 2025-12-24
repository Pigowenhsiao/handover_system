## ADDED Requirements
### Requirement: Persist data on application exit
The system SHALL flush in-progress edits and attempt to save report and attendance data before closing the application, and prompt for forced exit when persistence fails.

#### Scenario: Inline edit is flushed
- **WHEN** a user closes the application while an inline table edit is active
- **THEN** the edit is committed before exit proceeds

#### Scenario: Attendance changes are saved
- **WHEN** a user closes the application with modified attendance data
- **THEN** the system saves the attendance changes before exit proceeds

#### Scenario: Daily report summary is saved
- **WHEN** a user closes the application with daily report content entered
- **THEN** the system saves the daily report summary before exit proceeds

#### Scenario: Save failure offers forced exit
- **WHEN** the system cannot persist in-flight report or attendance data during close
- **THEN** the application prompts the user to force exit or stay open

#### Scenario: Pending imports offer forced exit
- **WHEN** there are pending import records that have not been uploaded
- **THEN** the application prompts the user to force exit or stay open

#### Scenario: Database path change forces restart
- **WHEN** a user updates the database path
- **THEN** the system attempts to save in-flight data, informs the user, and closes the application to require a restart
- **AND** if persistence fails, the user can choose whether to force close or keep the app open

#### Scenario: Initialize new database path
- **WHEN** a user selects a database path that does not exist
- **THEN** the system prompts whether to copy the current database or create a blank database file before restarting
