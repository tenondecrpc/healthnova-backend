## Why

Apple Health exports contain rich cardiovascular and activity data, but users have no way to upload and process these exports in HealthNova. We need a complete ingestion pipeline—from secure upload to parsed, queryable health records—before any analytics or risk scoring features can be built.

## What Changes

- Add `POST /upload/presigned-url` API endpoint to generate time-limited S3 presigned URLs scoped to the authenticated user's folder
- Add S3 bucket for health data exports with encryption, lifecycle policies, and event notifications
- Add Lambda function to process uploaded `export.zip` files: extract, stream-parse `exportar.xml`, parse ECG CSVs, and parse GPX workout routes
- Store normalized health records in DynamoDB using a single-table design
- Add Lambda layer with shared XML/ZIP/GPX parsing utilities
- Add IAM roles and policies for Lambda execution with least-privilege access to S3 and DynamoDB

## Capabilities

### New Capabilities

- `presigned-upload`: Generate authenticated, time-limited S3 presigned URLs for direct browser-to-S3 Apple Health export uploads
- `export-processing`: Extract and stream-parse Apple Health `export.zip` contents (XML health records, ECG CSVs, GPX workout routes) and persist normalized records to DynamoDB

### Modified Capabilities

_(none — this is greenfield infrastructure)_

## Impact

- **New AWS resources**: S3 bucket (healthnova-exports), DynamoDB table (health-records), 2 Lambda functions, Lambda layer, API Gateway routes
- **APIs introduced**: `POST /upload/presigned-url`
- **Dependencies**: `xmltodict` or streaming XML parser (Lambda layer), `boto3` (already available in Lambda runtime)
- **Security**: Presigned URLs expire in 1 hour (to accommodate large files on slow connections); S3 objects scoped to `{user_id}/` prefix; DynamoDB records keyed by `user_id`; encryption at rest and in transit; no PHI in logs
- **Cost estimate**: S3 (~$0.023/GB storage + $0.005/1k PUT requests), DynamoDB (on-demand, ~$1.25/million writes), Lambda (~$0.20/million invocations) — minimal for early stage
- **Data retention**: S3 exports archived to Glacier after 90 days; DynamoDB records retained indefinitely (user-controlled deletion planned in future)
