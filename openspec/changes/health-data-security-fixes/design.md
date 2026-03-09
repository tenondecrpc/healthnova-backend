## Context

The `health-data-ingestion` change shipped with five security defects surfaced during the post-implementation review:

1. **Wildcard IAM policies** — `S3Policy.ts` (`s3:*` on `*`) and `DynamoPolicy.ts` (`dynamodb:*` on `*`) are shared constructs attached to `presigned-url-upload`, `post-confirmation-signup`, and `process` Lambdas. This violates the least-privilege principle and grants full account-level S3/DynamoDB access to any compromised Lambda.

2. **`userId` is the raw S3 key** — The EventBridge rule target maps both `userId` and `jobId` via `$.detail.object.key`, which resolves to `exports/abc123/1700000000.zip` instead of `abc123`. Every DynamoDB health record ends up with a malformed PK (`USER#exports/...`), making the data unqueryable.

3. **Full in-memory ZIP load** — `validate-file` and `extract-manifest` call `s3_client.get_object(...).Body.read()` unconditionally, loading the entire export into Lambda memory (512 MB cap). A 500 MB+ export causes an OOM kill before any validation runs.

4. **Public photos bucket** — `publicReadAccess: true` with `blockPublicPolicy: false` exists with a TODO comment. Unacceptable for production in a HIPAA-aware system.

5. **Glue and observability gaps** — Glue job timeout (8 h) exceeds the state machine timeout (4 h), creating orphaned jobs. Glue continuous logging is not explicitly disabled, risking incidental data content in CloudWatch. The `log_lambda_event` utility logs a full JSON-serialized event payload — a latent PHI leak if applied to any ingestion Lambda.

## Goals / Non-Goals

**Goals:**
- Eliminate all CRITICAL and HIGH security findings
- Fix the data integrity bug (userId mapping) that corrupts DynamoDB keys
- Support the full 2 GB export size in validation without OOM
- Harden the photos bucket and Glue observability settings
- Remove or safe-replace the PHI-unsafe logger utility

**Non-Goals:**
- Adding customer-managed KMS keys to DynamoDB (tracked separately as L1 in security review)
- DynamoDB TTL for health records (future data retention policy change)
- Fixing CORS `allowedOrigins: '*'` on the exports bucket to a specific frontend domain (requires frontend URL to be known first)
- Any new features or pipeline changes

## Decisions

### 1. Per-Lambda scoped IAM policies — inline statements over shared constructs

The current `s3Policy` and `dynamoPolicy` constructs are reused for convenience but are dangerously overprivileged. The fix is to delete these constructs and define inline `PolicyStatement` objects at each Lambda's call site in `LambdaFactory`, matching the exact action set and resource ARN the Lambda actually needs.

**Alternative considered**: Restrict the shared constructs to narrower actions. Rejected — the shared construct pattern encourages copy-paste reuse and masks the resource scope. Inline statements make privilege visible at the point of use.

### 2. userId extraction — Lambda step vs. Step Functions JSONPath

S3 key format: `exports/{userId}/{timestamp}.zip`. The user ID is always the second path segment.

**Option A — Step Functions JSONPath/intrinsic**:
`States.ArrayGetItem(States.StringSplit($.detail.object.key, '/'), 1)` — available in Step Functions intrinsic functions, no extra Lambda, no cold start, zero cost.

**Option B — Extraction Lambda before ValidateFile**:
An extra Lambda step adds latency, cold starts, cost, and a new IAM execution role.

**Decision: Option A.** Use `sfn.JsonPath` with `States.StringSplit` intrinsic function in the EventBridge rule target input transform, or extract in the `ValidateFile` Lambda input itself using a Step Functions `Pass` state before the first Lambda step.

Implementation: Add a `ParseInput` Pass state as the first step that uses `States.StringSplit` to extract `userId` and derives `jobId` from the timestamp segment.

### 3. ZIP validation — byte-range requests for central directory

Python's `zipfile` module requires access to the ZIP End-of-Central-Directory record, which is located at the end of the file. For a well-formed ZIP, the central directory is at most ~65 KB from the end.

Approach:
1. `head_object` to get file size (already done).
2. `get_object(Range='bytes=-{65536}')` to fetch the last 64 KB.
3. Wrap in `io.BytesIO` and attempt `zipfile.ZipFile(...)` — valid ZIPs will parse their TOC from this fragment.
4. Enumerate `namelist()` to find `exportar.xml` and categorize ECG/GPX files.

**Limitation**: If the ZIP central directory exceeds 64 KB (extremely large file counts, e.g. 50k+ entries), the range read will miss it. In practice, Apple Health exports contain hundreds of files, not tens of thousands. Use 128 KB as the range to provide headroom.

**Alternative considered**: Download only the first N bytes (ZIP local file headers). Rejected — ZIP local headers don't reliably contain the full file list; the central directory at the end is the authoritative TOC.

### 4. Photos bucket — remove public access entirely

Remove `publicReadAccess`, set `blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL`. Photo access will be served via presigned GET URLs (same pattern as health exports). This is a no-regression change for the ingestion pipeline — the photos bucket is not used by any ingestion Lambda.

### 5. Glue hardening — align timeouts, disable continuous logging

- Set `timeout: 240` (4 hours) on the Glue job to match the state machine maximum.
- Add `'--enable-continuous-cloudwatch-log': 'false'` to `defaultArguments` to prevent Glue from streaming script output and potentially intermediate data to CloudWatch.
- Disable the job bookmark by default (`'--job-bookmark-option': 'job-bookmark-disable'`) since each execution processes a full export ZIP independently.

### 6. Logger utility — safe replacement

`log_lambda_event` will be replaced with `log_request_metadata`, which logs only safe, non-PHI fields: request ID, function name, remaining time, and event source/type. The full event dump is removed. Existing callers (`post-confirmation-signup`, `process`, `pre-signup`) must be updated to the new signature.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Byte-range ZIP read fails for unusual ZIP variants (e.g. ZIP64 with very large central directory) | Fall back to rejecting the file gracefully with a clear error; Glue job will catch legitimate archives if validation is overly strict |
| `States.StringSplit` intrinsic assumes `exports/{userId}/{timestamp}.zip` key format — a key format change would break extraction | Key format is enforced by `presigned-url-export` Lambda; document the format constraint explicitly |
| Removing `publicReadAccess` from photos bucket may break existing dev workflows that assumed public URLs | Coordinate with any local dev tooling; presigned GET URLs are a drop-in replacement |
| Updating `log_lambda_event` callers requires reading 3 Lambda files | Straightforward mechanical change; no behavioral impact |

## Migration Plan

1. Deploy CDK changes: IAM policy replacements, photos bucket hardening, Glue job defaults — no data migration required.
2. The `userId` fix is applied in the Step Functions state machine definition — new executions will use correct keys immediately. **Existing dev-environment DynamoDB records with malformed PKs should be manually flushed** (no production data exists yet).
3. Python Lambda changes (`validate-file`, `extract-manifest`, `logger.py`) deploy with the Lambda function code update — no rollback risk.
4. Rollback: all changes are infrastructure-as-code; `cdk deploy` of the previous commit restores prior state. DynamoDB records from the corrected deployment are incompatible with the old key schema — flush table if rolling back during dev.

## Open Questions

- What is the correct frontend origin for CORS `allowedOrigins`? (Needed to close M3 finding — currently deferred, `*` remains acceptable for non-production environments.)
- Should the `presigned-url-upload` Lambda (photos) also migrate to a scoped `s3:PutObject` policy once `publicReadAccess` is removed and presigned PUTs are introduced?
