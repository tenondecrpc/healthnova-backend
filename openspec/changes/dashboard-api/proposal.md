## Why

Health data is being ingested and stored in DynamoDB (heart rate, HRV, blood pressure, ECG, GPX workouts) but there are zero read endpoints. Users have no way to view their processed health records. The dashboard frontend cannot be built without a query API.

## What Changes

- Add `GET /dashboard/metrics` endpoint with scatter-gather across 10 DynamoDB shards, supporting raw and daily-aggregated granularity
- Add `GET /dashboard/ecg` endpoint for paginated ECG record queries
- Add `GET /dashboard/workouts` endpoint for paginated GPX workout route queries
- Add `GET /dashboard/jobs` endpoint for ingestion job status history
- Add `GET /dashboard/summary` composite endpoint aggregating key metrics (HeartRate, HRV, BloodPressure), ECG count, workout count, and recent jobs over the last 7 days
- Add 5 new Lambda functions under `src/lambda/dashboard/`
- Add CDK infrastructure to wire routes, IAM policies, and environment variables

## Capabilities

### New Capabilities

- `dashboard-metrics`: Query health metrics by type with scatter-gather across 10 DynamoDB shards, supporting raw paginated and daily-aggregated (avg/min/max/count) granularity within 90-day windows
- `dashboard-ecg`: Query ECG records with pagination and date range filtering
- `dashboard-workouts`: Query GPX workout routes with pagination and date range filtering
- `dashboard-jobs`: View ingestion job history and status
- `dashboard-summary`: On-demand composite endpoint that aggregates HeartRate, HRV, BloodPressure, ECG count, workout count, and recent jobs for the last 7 days

### Modified Capabilities

- REST API factory gains 5 new authenticated routes under `/dashboard/`
- Lambda factory gains 5 new Lambda function definitions

## Impact

- **New AWS resources**: 5 Lambda functions (Python, shared layer)
- **APIs introduced**: `GET /dashboard/metrics`, `GET /dashboard/ecg`, `GET /dashboard/workouts`, `GET /dashboard/jobs`, `GET /dashboard/summary`
- **Dependencies**: No new external dependencies — uses existing `boto3` and `common` layer
- **Security**: All endpoints require Cognito authentication; queries scoped to authenticated user's records only (`USER#{userId}`); no PHI in logs; date range capped at 90 days to prevent expensive full-table scans
- **Cost estimate**: Lambda invocations (~$0.20/million); DynamoDB reads (~$0.25/million read units); summary endpoint uses up to 32 parallel queries per invocation (30 shard queries + ECG + GPX)
- **No new tables or GSIs**: All queries use existing `healthRecordsTable` keys and the `UserTypeIndex` GSI

## Future Implementations

- **LLM Disease Detection**: A separate daily asynchronous process that will query the last 90 days of a user's health records and pass them to a Large Language Model (LLM) to detect potential anomalies or early signs of diseases. This will operate within the maximum 90-day query limit established in this API.
