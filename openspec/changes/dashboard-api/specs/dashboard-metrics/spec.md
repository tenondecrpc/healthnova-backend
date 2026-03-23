## ADDED Requirements

### Requirement: Query health metrics by type with date range
The system SHALL expose a `GET /dashboard/metrics` endpoint that returns health metric records for the authenticated user, queried by record type and date range.

#### Scenario: Daily aggregation (default)
- **WHEN** an authenticated user requests `GET /dashboard/metrics?type=HeartRate&start=2024-01-01&end=2024-01-31`
- **THEN** the system returns daily aggregates (avg, min, max, count) sorted by date, with the metric unit and period metadata

#### Scenario: Raw paginated records
- **WHEN** an authenticated user requests `GET /dashboard/metrics?type=HeartRate&start=2024-01-01&end=2024-01-31&granularity=raw`
- **THEN** the system returns individual records sorted by startDate, limited to 100 per page by default, with a `nextCursor` for pagination

#### Scenario: Custom limit for raw mode
- **WHEN** an authenticated user requests raw granularity with `limit=500`
- **THEN** the system returns up to 500 records per page, capped at a maximum of 1000

#### Scenario: Cursor-based pagination for raw mode
- **WHEN** an authenticated user provides a `cursor` parameter from a previous response
- **THEN** the system resumes the query across all shards from the encoded position

### Requirement: Scatter-gather across DynamoDB shards
The system SHALL fan out queries to all 10 DynamoDB shards (`USER#{userId}#SHARD#0` through `USER#{userId}#SHARD#9`) in parallel and merge results.

#### Scenario: Parallel shard queries
- **WHEN** a metrics query is executed
- **THEN** the system issues 10 DynamoDB Query calls in parallel (one per shard) with `SK between RECORD#{type}#{start}` and `RECORD#{type}#{end}`

#### Scenario: All shards return empty
- **WHEN** no records exist for the requested type and date range
- **THEN** the system returns an empty `data` array with the period metadata

#### Scenario: Partial shard results
- **WHEN** some shards contain records and others are empty
- **THEN** the system merges available results and omits exhausted shards from the pagination cursor

### Requirement: Validate metric query parameters
The system SHALL validate all query parameters and reject invalid requests.

#### Scenario: Missing required parameters
- **WHEN** `type`, `start`, or `end` is missing
- **THEN** the system returns HTTP 400 with an error message identifying the missing parameter

#### Scenario: Date range exceeds 90 days
- **WHEN** the difference between `start` and `end` exceeds 90 days
- **THEN** the system returns HTTP 400 with error code `DATE_RANGE_EXCEEDED`

#### Scenario: Invalid metric type
- **WHEN** `type` is not in the allowed metric types whitelist
- **THEN** the system returns HTTP 400 with error code `INVALID_METRIC_TYPE`

#### Scenario: Unauthenticated request
- **WHEN** a request is made without a valid Cognito token
- **THEN** the system returns HTTP 401

### Requirement: No PHI in logs
The system SHALL never log health record values in CloudWatch.

#### Scenario: Request logging
- **WHEN** a metrics query is processed
- **THEN** logs contain only the metric type, date range, record count, and execution time — never record values
