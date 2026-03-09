## 1. Infrastructure — S3 & DynamoDB

- [x] 1.1 Create CDK construct for S3 exports bucket with SSE-S3 encryption, versioning, and `exports/` prefix structure
- [x] 1.2 Add S3 lifecycle rule to transition objects in `exports/` to Glacier after 90 days
- [x] 1.3 Create CDK construct for DynamoDB health-records table: `PK=USER#{user_id}`, `SK=RECORD#{type}#{timestamp}`, on-demand capacity, encryption at rest
- [x] 1.4 Add GSI `UserTypeIndex` on `(PK, SK)` to support time-range queries by record type
- [x] 1.5 Add unit tests for CDK constructs (snapshot tests)

## 2. Presigned Upload — Lambda & API Gateway

- [x] 2.1 Implement `src/lambda/upload/presigned_url.py`: generate S3 presigned PUT URL scoped to `exports/{user_id}/{timestamp}.zip`, 1-hour expiry (to accommodate large files on slow connections)
- [x] 2.2 Add IAM policy restricting the Lambda execution role to `s3:PutObject` on `exports/{user_id}/*` using condition key `s3:prefix`
- [x] 2.3 Add Cognito authorizer to API Gateway and wire `POST /upload/presigned-url` route to the Lambda
- [x] 2.4 Write unit tests for presigned URL Lambda (mock S3 client, assert URL scope and expiry)
- [x] 2.5 Document `EXPORTS_BUCKET_NAME` and `PRESIGNED_URL_EXPIRY_SECONDS` environment variables in `.env.example`

## 3. Infrastructure — EventBridge & Step Functions

- [x] 3.1 Add EventBridge rule to capture `s3:ObjectCreated:*` events on the exports bucket filtered to `exports/` prefix and `.zip` suffix
- [x] 3.2 Define Step Functions Standard Workflow CDK construct with states: `ValidateFile → ExtractManifest → Parallel(ParseXML, ParseECG, ParseGPX) → MarkComplete`
- [x] 3.3 Add CloudWatch alarm for Step Functions executions exceeding 4 hours
- [x] 3.4 Add unit tests for state machine definition (CDK snapshot)

## 4. Validation & Manifest Lambda

- [x] 4.1 Implement `src/lambda/ingestion/validate_file.py`: check ZIP integrity, verify `exportar.xml` presence, reject files >2GB
- [x] 4.2 Implement `src/lambda/ingestion/extract_manifest.py`: list files inside the ZIP (XML, ECG CSVs, GPX routes) and return file inventory as Step Functions output
- [x] 4.3 Implement `src/lambda/ingestion/mark_complete.py`: write final job status (`COMPLETED` or `FAILED`) to DynamoDB
- [x] 4.4 Write unit tests for validate and manifest Lambdas (test malformed ZIP, missing XML, oversized file)

## 5. Glue Job — XML Parsing

- [x] 5.1 Write Glue Python Shell script `src/glue/parse_health_xml.py`: stream-read `exportar.xml` from S3 ZIP using `iterparse`, extract health record entries (heart rate, HRV, blood pressure, SpO2, sleep)
- [x] 5.2 Implement DynamoDB batch writer in the Glue script with exponential backoff for throttled writes
- [x] 5.3 Create CDK construct for the Glue job: Python Shell worker (0.0625 DPU), IAM role with least-privilege S3 read and DynamoDB write access
- [x] 5.4 Ensure no health record field values are written to Glue logs — log counts and durations only
- [x] 5.5 Write unit tests for the XML parser logic (mock S3 stream, assert DynamoDB write calls)

## 6. ECG & GPX Lambda Functions

- [x] 6.1 Implement `src/lambda/ingestion/parse_ecg.py`: read ECG CSV files from ZIP, parse voltage/classification columns, write ECG records to DynamoDB
- [x] 6.2 Implement `src/lambda/ingestion/parse_gpx.py`: read GPX workout route files from ZIP, extract waypoints, write route records to DynamoDB
- [x] 6.3 Write unit tests for ECG Lambda (assert correct DynamoDB key format, handle missing files)
- [x] 6.4 Write unit tests for GPX Lambda (assert waypoint parsing, handle empty routes)

## 7. IAM Policies

- [x] 7.1 Create shared IAM policy construct in `lib/stack/shared/policy/` for DynamoDB write access scoped to `USER#{user_id}` partition
- [x] 7.2 Create IAM policy for Glue job execution role: `s3:GetObject` on exports bucket, `dynamodb:BatchWriteItem` on health-records table
- [x] 7.3 Review all Lambda execution roles — confirm no wildcard resource ARNs

## 8. Integration & End-to-End Tests

- [x] 8.1 Write integration test: upload a sample export.zip via presigned URL and assert Step Functions execution reaches `COMPLETED` state
- [x] 8.2 Write integration test: upload malformed ZIP and assert job status is set to `FAILED` in DynamoDB
- [x] 8.3 Verify CloudWatch logs contain no PHI across all Lambda and Glue job executions
