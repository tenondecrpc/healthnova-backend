## Why

A security review of the `health-data-ingestion` change identified issues that must be resolved before production: wildcard IAM policies granting full S3/DynamoDB access to multiple Lambdas, a data integrity bug that corrupts all DynamoDB health record keys, and memory exhaustion in the ZIP validation path that blocks processing of any export over ~400 MB.

## What Changes

- Replace wildcard `s3:*` and `dynamodb:*` shared policies with resource-scoped `PolicyStatement`s per Lambda
- Fix the EventBridge → Step Functions input mapping to extract the real `userId` from the S3 object key path instead of passing the raw key as the user ID
- Refactor `validate-file` and `extract-manifest` Lambdas to use S3 byte-range requests for the ZIP central directory, eliminating the full in-memory load
- Remove `publicReadAccess: true` from the photos bucket and restore `BlockPublicAccess.BLOCK_ALL`
- Align Glue job timeout with the state machine timeout (both ≤ 4 hours) and explicitly disable Glue continuous logging
- Deprecate the `log_lambda_event` utility that dumps raw Lambda events to CloudWatch — a latent PHI leakage risk

## Capabilities

### New Capabilities

- `iam-scoped-policies`: Remove shared wildcard IAM policies and replace with per-Lambda, resource-scoped policy statements
- `sfn-userid-extraction`: Fix Step Functions input mapping to parse `userId` from the S3 key path segment rather than using the full key string
- `zip-stream-validation`: Refactor ZIP validation and manifest extraction to stream only the ZIP central directory via S3 byte-range requests, supporting exports up to 2 GB without memory issues
- `s3-hardening`: Remove public access from the photos bucket and scope CORS `allowedOrigins` to the application domain instead of `*`
- `observability-hardening`: Align Glue/state machine timeouts, disable Glue continuous logging for data content, and replace the PHI-unsafe `log_lambda_event` utility with a metadata-only version

### Modified Capabilities

- `presigned-upload`: No requirement change — only the IAM policy implementation changes (already covered under `iam-scoped-policies`)

## Impact

- **Files modified**: `lib/stack/shared/policy/S3Policy.ts`, `lib/stack/shared/policy/DynamoPolicy.ts`, `lib/stack/lambda/index.ts`, `lib/stack/step-functions/index.ts`, `lib/stack/glue/index.ts`, `lib/stack/s3/index.ts`, `src/lambda/ingestion/validate-file/index.py`, `src/lambda/ingestion/extract-manifest/index.py`, `src/layer/python-common/python/common/logger.py`
- **APIs changed**: None — all changes are infrastructure and implementation
- **Breaking changes**: None for external consumers; DynamoDB record PKs will be written correctly going forward (existing records from dev testing have malformed keys and should be flushed)
- **Security posture**: Eliminates all CRITICAL and HIGH findings from the security review; addresses 3 of 5 MEDIUM findings
- **Cost impact**: Negligible — byte-range reads slightly reduce S3 data transfer for validation; no new services introduced
