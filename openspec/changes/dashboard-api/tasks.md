## 1. Shared Query Utilities

- [ ] 1.1 Create `src/lambda/dashboard/shared/query_utils.py` with scatter-gather helper: accepts userId, recordType, startDate, endDate, and executes 10 parallel DynamoDB queries (one per shard) using `concurrent.futures.ThreadPoolExecutor`, merging and sorting results by `startDate`
- [ ] 1.2 Create `src/lambda/dashboard/shared/pagination.py` with cursor encoding/decoding: base64 JSON containing per-shard `LastEvaluatedKey` objects; handle shard exhaustion (omit from cursor)
- [ ] 1.3 Create `src/lambda/dashboard/shared/validation.py` with date range validation: parse ISO dates, enforce max 90-day window, validate metric type against allowed types whitelist, validate limit bounds
- [ ] 1.4 Create `src/lambda/dashboard/shared/aggregation.py` with daily aggregation: group records by date, compute avg/min/max/count per day, return sorted list
- [ ] 1.5 Write unit tests for query_utils, pagination, validation, and aggregation modules

## 2. Dashboard Metrics Lambda

- [ ] 2.1 Implement `src/lambda/dashboard/get-metrics/index.py`: parse query params (type, start, end, granularity, limit, cursor), validate inputs, call scatter-gather, apply aggregation or pagination based on granularity, return formatted response using `common` layer
- [ ] 2.2 Write unit tests for get-metrics Lambda (mock DynamoDB, test daily aggregation, test raw pagination, test validation errors, test empty results)

## 3. Dashboard ECG Lambda

- [ ] 3.1 Implement `src/lambda/dashboard/get-ecg/index.py`: parse query params (start, end, limit, cursor), query `PK=USER#{userId}` with `SK begins_with RECORD#ECG#` filtered by date range, return paginated response
- [ ] 3.2 Write unit tests for get-ecg Lambda (mock DynamoDB, test pagination, test date filtering, test empty results)

## 4. Dashboard Workouts Lambda

- [ ] 4.1 Implement `src/lambda/dashboard/get-workouts/index.py`: parse query params (start, end, limit, cursor), query `PK=USER#{userId}` with `SK begins_with RECORD#GPX#` filtered by date range, return paginated response
- [ ] 4.2 Write unit tests for get-workouts Lambda (mock DynamoDB, test pagination, test date filtering, test empty results)

## 5. Dashboard Jobs Lambda

- [ ] 5.1 Implement `src/lambda/dashboard/get-jobs/index.py`: query `PK=USER#{userId}` with `SK begins_with JOB#`, sort by `updatedAt` desc, limit 20, return job list
- [ ] 5.2 Write unit tests for get-jobs Lambda (mock DynamoDB, test sorting, test empty results)

## 6. Dashboard Summary Lambda

- [ ] 6.1 Implement `src/lambda/dashboard/get-summary/index.py`: compute last-7-days period, execute in parallel: scatter-gather for HeartRate + HeartRateVariabilitySDNN + BloodPressureSystolic (30 queries), ECG count query, GPX count query, jobs query (limit 5); aggregate each metric type into avg/min/max/count; return composite response
- [ ] 6.2 Write unit tests for get-summary Lambda (mock DynamoDB, test aggregation, test partial failures, test empty data)

## 7. CDK Infrastructure

- [ ] 7.1 Add 5 Lambda function definitions to `LambdaFactory` (`lib/stack/lambda/index.ts`): `getDashboardMetricsLambda`, `getDashboardEcgLambda`, `getDashboardWorkoutsLambda`, `getDashboardJobsLambda`, `getDashboardSummaryLambda` — all with `HEALTH_RECORDS_TABLE_NAME` env var and `python-common` layer
- [ ] 7.2 Create IAM policy for dashboard Lambdas: `dynamodb:Query` on `healthRecordsTable` ARN and its `UserTypeIndex` GSI ARN, scoped to read-only
- [ ] 7.3 Add 5 routes to `RestApiFactory` (`lib/stack/rest-api/index.ts`): `GET /dashboard/metrics`, `GET /dashboard/ecg`, `GET /dashboard/workouts`, `GET /dashboard/jobs`, `GET /dashboard/summary` — all with `requireAuth: true`
- [ ] 7.4 Run `npm run build && npx cdk synth` to validate the CDK stack compiles and synthesizes
- [ ] 7.5 Write CDK snapshot tests for the new Lambda functions and API Gateway routes
