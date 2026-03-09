## ADDED Requirements

### Requirement: Step Functions execution receives correct userId from S3 key
When an export ZIP upload triggers the ingestion workflow, the Step Functions execution input SHALL contain the authenticated user's ID as a plain string (e.g. `abc123`), not the full S3 object key (`exports/abc123/1700000000.zip`).

#### Scenario: userId is extracted from the S3 key path segment
- **WHEN** S3 fires an `Object Created` event for key `exports/abc123/1700000000.zip`
- **THEN** the Step Functions execution receives `userId = "abc123"` in its input

#### Scenario: jobId is derived from the upload timestamp segment
- **WHEN** S3 fires an `Object Created` event for key `exports/abc123/1700000000.zip`
- **THEN** the Step Functions execution receives `jobId = "1700000000"` in its input

#### Scenario: DynamoDB health records have well-formed partition key
- **WHEN** the ingestion workflow completes successfully
- **THEN** all DynamoDB items written for the user have `PK = "USER#abc123"` — not `PK = "USER#exports/abc123/1700000000.zip"`

#### Scenario: userId extraction is resilient to key format
- **WHEN** the S3 key does not match the expected `exports/{userId}/{timestamp}.zip` pattern
- **THEN** the workflow fails at the input parsing step with a descriptive error before any Lambda is invoked
