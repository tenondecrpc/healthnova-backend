## ADDED Requirements

### Requirement: List ingestion job history
The system SHALL expose a `GET /dashboard/jobs` endpoint that returns the authenticated user's ingestion job history.

#### Scenario: Jobs returned sorted by most recent
- **WHEN** an authenticated user requests `GET /dashboard/jobs`
- **THEN** the system returns up to 20 job records (jobId, status, updatedAt) sorted by `updatedAt` descending

#### Scenario: No jobs exist
- **WHEN** the user has no ingestion job records
- **THEN** the system returns an empty `data` array

#### Scenario: Multiple job statuses
- **WHEN** the user has jobs in COMPLETED, FAILED, and PROCESSING states
- **THEN** all jobs are returned regardless of status, sorted by `updatedAt` descending

### Requirement: Direct query without scatter-gather
The system SHALL query job records using a single DynamoDB Query on `PK=USER#{userId}` with `SK begins_with JOB#`, since job records are not sharded.

#### Scenario: Single partition query
- **WHEN** a jobs query is executed
- **THEN** the system issues a single DynamoDB Query (not fan-out to multiple shards)

### Requirement: Unauthenticated access is rejected
The system SHALL require Cognito authentication for the jobs endpoint.

#### Scenario: Unauthenticated request
- **WHEN** a request is made without a valid Cognito token
- **THEN** the system returns HTTP 401
