## ADDED Requirements

### Requirement: Glue job timeout does not exceed state machine timeout
The `parse-health-xml` Glue job timeout SHALL be set to 240 minutes (4 hours) or less, ensuring it cannot outlive the Step Functions state machine that launches it.

#### Scenario: Glue job timeout is aligned with state machine timeout
- **WHEN** the CDK stack is synthesized
- **THEN** the `parse-health-xml` Glue job `timeout` property SHALL be ≤ 240 minutes

#### Scenario: No orphaned Glue jobs after state machine timeout
- **WHEN** the Step Functions state machine reaches its 4-hour timeout and transitions to a `TimedOut` state
- **THEN** no Glue job instance for that execution can still be running (because the Glue job timeout is ≤ state machine timeout)

### Requirement: Glue continuous logging is disabled
The `parse-health-xml` Glue job SHALL explicitly disable continuous CloudWatch logging to prevent intermediate script output or data content from appearing in log streams.

#### Scenario: Glue job default arguments disable continuous logging
- **WHEN** the CDK stack is synthesized
- **THEN** the Glue job `defaultArguments` SHALL contain `'--enable-continuous-cloudwatch-log': 'false'`

### Requirement: Logger utility does not log full Lambda event payloads
The `log_lambda_event` function in the shared Lambda layer SHALL be removed or replaced with a `log_request_metadata` function that logs only non-PHI metadata: AWS request ID, function name, remaining execution time, and event source/type.

#### Scenario: log_request_metadata logs only safe metadata fields
- **WHEN** `log_request_metadata` is called with a Lambda event and context
- **THEN** the log output contains only: `request_id`, `function_name`, `remaining_ms`, and optionally `event_source` — no raw event body, no user attributes, no health data

#### Scenario: Full event body is not logged by any shared utility
- **WHEN** any ingestion Lambda function executes
- **THEN** no CloudWatch log line contains the serialized event payload from `json.dumps(event, ...)` or equivalent full event serialization
