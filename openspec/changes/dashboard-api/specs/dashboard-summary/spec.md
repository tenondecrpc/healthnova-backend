## ADDED Requirements

### Requirement: Composite health summary for last 7 days
The system SHALL expose a `GET /dashboard/summary` endpoint that returns an on-demand aggregated summary of the authenticated user's key health metrics, ECG count, workout count, and recent jobs for the last 7 days.

#### Scenario: Full summary with all data types
- **WHEN** an authenticated user requests `GET /dashboard/summary` and has data across all types
- **THEN** the system returns: HeartRate aggregates (avg, min, max, count), HRV aggregates (avg, min, max, count), BloodPressure aggregates (avgSystolic, avgDiastolic, count), ECG record count, workout count, and up to 5 most recent jobs

#### Scenario: Partial data available
- **WHEN** the user has HeartRate data but no ECG or GPX records
- **THEN** the system returns HeartRate aggregates with non-null values, and zero counts for ECG and workouts

#### Scenario: No data at all
- **WHEN** the user has no health records in the last 7 days
- **THEN** the system returns null aggregates for metrics and zero counts for ECG/workouts

### Requirement: Parallel query execution
The system SHALL execute all summary sub-queries in parallel to minimize latency.

#### Scenario: Parallel execution
- **WHEN** a summary request is processed
- **THEN** the system executes up to 32 DynamoDB queries in parallel: HeartRate scatter-gather (10), HRV scatter-gather (10), BloodPressure scatter-gather (10), ECG count (1), GPX count (1)

### Requirement: On-demand computation (no pre-computation)
The system SHALL compute summaries at request time by querying DynamoDB directly. No pre-computed aggregation tables are used.

#### Scenario: Fresh data reflected immediately
- **WHEN** new health records are ingested and the user requests a summary
- **THEN** the summary reflects the newly ingested data without delay

### Requirement: Unauthenticated access is rejected
The system SHALL require Cognito authentication for the summary endpoint.

#### Scenario: Unauthenticated request
- **WHEN** a request is made without a valid Cognito token
- **THEN** the system returns HTTP 401
