## ADDED Requirements
### Requirement: Report pages require login
The system SHALL block access to attendance summary, summary query, and abnormal history pages when no user is logged in.

#### Scenario: Block unauthenticated access
- **WHEN** a user attempts to open attendance summary, summary query, or abnormal history without logging in
- **THEN** the system prevents navigation and prompts the user to log in

#### Scenario: Allow access without daily report context
- **WHEN** a logged-in user opens attendance summary, summary query, or abnormal history without saving daily report basic info
- **THEN** the system allows access to the report page

### Requirement: Daily report selections start blank
The system SHALL leave shift and area unselected when opening or resetting a daily report.

#### Scenario: Daily report opens with blank selections
- **WHEN** the daily report page is opened
- **THEN** the shift and area fields are empty until the user selects values

#### Scenario: Daily report reset clears selections
- **WHEN** the user resets the daily report
- **THEN** the shift and area fields are cleared
