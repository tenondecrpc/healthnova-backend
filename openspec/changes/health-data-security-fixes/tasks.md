## 1. IAM Scoped Policies (CRITICAL — C1)

- [x] 1.1 Delete `lib/stack/shared/policy/S3Policy.ts` — remove the wildcard `s3:*` on `*` shared construct
- [x] 1.2 Delete `lib/stack/shared/policy/DynamoPolicy.ts` — remove the wildcard `dynamodb:*` on `*` shared construct
- [x] 1.3 Update `lib/stack/shared/policy/index.ts` to remove exports for the deleted policy files
- [x] 1.4 In `lib/stack/lambda/index.ts`, replace `dynamoPolicy` on `postConfirmationSignupLambda` with a scoped `PolicyStatement`: `dynamodb:PutItem` on `userTable.tableArn`
- [x] 1.6 In `lib/stack/lambda/index.ts`, replace `dynamoPolicy` on `processLambda` with a scoped `PolicyStatement`: `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:UpdateItem`, `dynamodb:Query` on `processTable.tableArn`
- [x] 1.7 Run `npm run build && npx cdk synth` and verify no `"Action": "s3:*"` or `"Action": "dynamodb:*"` with `"Resource": "*"` appear in the synthesized template
- [x] 1.8 Update `test/lambda/presigned-url-export.test.ts` and add tests for the new scoped policies on `post-confirmation-signup` and `process` Lambdas

## 2. Step Functions userId Extraction (HIGH — H1)

- [x] 2.1 In `lib/stack/step-functions/index.ts`, add a `ParseInput` Pass state as the first step in the state machine that uses `States.StringSplit` and `States.ArrayGetItem` intrinsic functions to extract `userId` (segment index 1) and `jobId` (segment index 2, strip `.zip`) from the S3 key
- [x] 2.2 Update the EventBridge rule target input to pass `bucket`, `key`, and `rawKey` — move `userId`/`jobId` extraction into the `ParseInput` Pass state instead of the rule target
- [x] 2.3 Update the chain: `ParseInput → validateFile → extractManifest → parallelParsing → markComplete`
- [x] 2.4 Add a test in `test/step-functions/ingestion-workflow.test.ts` verifying the state machine definition contains the `ParseInput` state
- [x] 2.5 Flush any dev-environment DynamoDB `health-records` table records with malformed `PK` values (keys starting with `USER#exports/`) — document the flush command
  > Flush command: `aws dynamodb scan --table-name healthnova-dev-health-records --filter-expression "begins_with(PK, :pfx)" --expression-attribute-values '{":pfx":{"S":"USER#exports/"}}' --query "Items[].{PK:PK.S,SK:SK.S}" | jq -r '.[] | "--request-id \(.PK) \(.SK)"'` then delete each item via `aws dynamodb delete-item`.

## 3. ZIP Stream Validation (HIGH — H2)

- [x] 3.1 Refactor `src/lambda/ingestion/validate-file/index.py`: replace `get_object(...).Body.read()` with an `_S3SeekableStream` that issues byte-range requests on demand
- [x] 3.2 In `validate-file`, `_S3SeekableStream` wrapped by `zipfile.ZipFile` reads only central directory bytes; `BadZipFile` is caught and re-raised as `ValueError`
- [x] 3.3 Refactor `src/lambda/ingestion/extract-manifest/index.py` with the same byte-range stream approach
- [x] 3.4 Add a unit test for `validate-file` that patches `s3_client.get_object` and asserts every call includes a `Range` header (no full-body read) — `src/lambda/ingestion/validate-file/test_index.py`
- [x] 3.5 Add a unit test for `extract-manifest` with the same range-request assertion, verifying ECG/GPX/XML file categorization still works correctly — `src/lambda/ingestion/extract-manifest/test_index.py`

## 4. S3 Bucket Hardening (HIGH — H3)

- [x] 4.1 In `lib/stack/s3/index.ts`, remove `publicReadAccess: true` from the photos bucket configuration
- [x] 4.2 Replace the partial `BlockPublicAccess` config on the photos bucket with `s3.BlockPublicAccess.BLOCK_ALL`
- [x] 4.3 Remove the TODO comments about public access now that it is resolved
- [x] 4.4 Run `npx cdk synth` and confirm the photos bucket `PublicAccessBlockConfiguration` has all four properties set to `true`
- [x] 4.5 Add a test in `test/s3/photos-bucket.test.ts` verifying the photos bucket blocks all public access

## 5. Observability Hardening (MEDIUM — M4, M5, L3)

- [x] 5.1 In `lib/stack/glue/index.ts`, change the Glue job `timeout` from `480` to `240` (4 hours, matching state machine timeout)
- [x] 5.2 In `lib/stack/glue/index.ts`, add `'--enable-continuous-cloudwatch-log': 'false'` and `'--job-bookmark-option': 'job-bookmark-disable'` to the Glue job `defaultArguments`
- [x] 5.3 In `src/layer/python-common/python/common/logger.py`, remove the `log_lambda_event` function
- [x] 5.4 Add a replacement `log_request_metadata(logger, context)` function that logs only: `request_id`, `function_name`, `remaining_ms` — no event body
- [x] 5.5 Update `src/layer/python-common/python/common/__init__.py` to remove `log_lambda_event` from exports and add `log_request_metadata`
- [x] 5.6 Update `src/lambda/user/post-confirmation-signup/index.py` — replace `log_lambda_event` call with `log_request_metadata`
- [x] 5.7 Update `src/lambda/core/process/index.py` — replace `log_lambda_event` call with `log_request_metadata`
- [x] 5.8 Update `src/lambda/user/pre-signup/index.py` — replace `log_lambda_event` call with `log_request_metadata`
- [x] 5.9 Update test for `glue/parse-health-xml.test.ts` to verify the `timeout` is 240 and `defaultArguments` includes the logging flag

## 6. Verification

- [x] 6.1 Run full test suite (`npm test`) — all tests pass (7 suites, 25 tests)
- [x] 6.2 Run `npx cdk synth` — no synthesis errors; zero wildcard IAM actions in template
- [x] 6.3 Run `npx cdk diff` — review the changeset confirms: no new `*` IAM resources, photos bucket policy updated, Glue job properties updated, state machine definition updated
- [x] 6.4 Re-run `/opsx:security health-data-security-fixes` — confirm CRITICAL and HIGH findings are resolved
