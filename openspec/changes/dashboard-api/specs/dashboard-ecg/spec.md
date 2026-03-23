## ADDED Requirements

### Requirement: Query ECG records with date range
The system SHALL expose a `GET /dashboard/ecg` endpoint that returns paginated ECG records for the authenticated user within a date range.

#### Scenario: ECG records returned with pagination
- **WHEN** an authenticated user requests `GET /dashboard/ecg?start=2024-01-01&end=2024-01-31`
- **THEN** the system returns ECG records (timestamp, classification, averageHeartRate) sorted by timestamp, limited to 50 per page by default, with a `nextCursor` for pagination

#### Scenario: Custom limit
- **WHEN** an authenticated user provides `limit=100`
- **THEN** the system returns up to 100 records per page, capped at a maximum of 200

#### Scenario: Cursor-based pagination
- **WHEN** an authenticated user provides a `cursor` parameter from a previous response
- **THEN** the system resumes the query from the encoded DynamoDB `LastEvaluatedKey`

#### Scenario: No ECG records in range
- **WHEN** no ECG records exist within the requested date range
- **THEN** the system returns an empty `data` array with the period metadata

### Requirement: Direct query without scatter-gather
The system SHALL query ECG records using a single DynamoDB Query on `PK=USER#{userId}` with `SK begins_with RECORD#ECG#`, since ECG records are not sharded.

#### Scenario: Single partition query
- **WHEN** an ECG query is executed
- **THEN** the system issues a single DynamoDB Query (not fan-out to multiple shards)

### Requirement: Validate ECG query parameters
The system SHALL validate all query parameters and reject invalid requests.

#### Scenario: Missing required date parameters
- **WHEN** `start` or `end` is missing
- **THEN** the system returns HTTP 400 with an error message identifying the missing parameter

#### Scenario: Date range exceeds 90 days
- **WHEN** the difference between `start` and `end` exceeds 90 days
- **THEN** the system returns HTTP 400 with error code `DATE_RANGE_EXCEEDED`

#### Scenario: Unauthenticated request
- **WHEN** a request is made without a valid Cognito token
- **THEN** the system returns HTTP 401
