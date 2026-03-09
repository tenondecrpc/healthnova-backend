# Security Review: health-data-ingestion

**Date**: 2026-03-09
**Reviewer**: AI Security Analysis
**Status**: ⚠️ WARNINGS

---

## Executive Summary

The `health-data-ingestion` change demonstrates solid security intent throughout: IAM policies for ingestion Lambdas are properly scoped, PHI is not logged in any ingestion code path, encryption is enabled at rest and in transit, and Cognito auth gates the presigned URL endpoint. No CRITICAL issues exist within the ingestion pipeline itself.

However, **two pre-existing wildcard IAM policies** (`S3Policy.ts`, `DynamoPolicy.ts`) grant full service-level access to other Lambdas in the same stack — a CRITICAL risk that must be addressed before production. Additionally, a **data integrity bug** in the EventBridge → Step Functions mapping sets `userId` to the raw S3 key instead of the extracted user ID, which would corrupt all DynamoDB record keys.

---

## Findings

### CRITICAL

- [ ] **C1 — Wildcard IAM policies on `s3Policy` and `dynamoPolicy`**
  - `lib/stack/shared/policy/S3Policy.ts`: `s3:*` on `*`
  - `lib/stack/shared/policy/DynamoPolicy.ts`: `dynamodb:*` on `*`
  - These policies are attached to `presignedUrlUploadLambda`, `postConfirmationSignupLambda`, and `processLambda`. Any compromise of these Lambdas grants full S3/DynamoDB access to the entire AWS account, including the health-records table with PHI.
  - **Not introduced by this change**, but exist in the same stack and must be remediated before production.
  - Remediation: Scope each policy to the specific bucket ARN / table ARN the Lambda actually needs.

### HIGH

- [ ] **H1 — `userId` in Step Functions input is set to the raw S3 key**
  - `lib/stack/step-functions/index.ts:150-151`
  - Both `userId` and `jobId` are mapped via `events.EventField.fromPath('$.detail.object.key')`, which resolves to the full S3 object key (e.g. `exports/abc123/1700000000.zip`), not the user ID.
  - Consequence: all DynamoDB records written by ingestion Lambdas get `PK = USER#exports/abc123/1700000000.zip`, making all health data unqueryable by user. Job tracking is also broken.
  - Remediation: Extract the user ID from the S3 key path segment. Use a Lambda or Step Functions `States.StringSplit` / JSONPath to parse `exports/{userId}/{timestamp}.zip`.

- [ ] **H2 — `validate-file` and `extract-manifest` load entire ZIP into memory**
  - `src/lambda/ingestion/validate-file/index.py:34` and `extract-manifest/index.py:22`
  - Both Lambdas call `obj["Body"].read()` which buffers the full ZIP in memory. With 512 MB of Lambda memory and a 2 GB max file size, any upload over ~400 MB will OOM-kill the Lambda.
  - The `head_object` size check (correct) runs before the read, but a valid 500 MB file is still unprocessable.
  - Remediation: Stream only the ZIP central directory (last ~64 KB) using S3 byte-range requests (`Range: bytes=-65536`) to read the TOC without loading the file body. The Python `zipfile` module supports this via `seekable` streams.

- [ ] **H3 — Photos bucket has public read access**
  - `lib/stack/s3/index.ts:27-42` — `publicReadAccess: true`, `blockPublicPolicy: false`
  - Two TODO comments acknowledge this is temporary. The photos bucket is in the same stack as the health exports bucket. While health data is in a separate, private bucket, this represents an unacceptable production posture for a HIPAA-aware system.
  - Remediation: Remove `publicReadAccess: true`, restore `BlockPublicAccess.BLOCK_ALL`, and serve photos via presigned URLs.

### MEDIUM

- [ ] **M1 — `userId` / `jobId` not extracted from S3 key — workaround needed in Lambdas**
  - Related to H1. Downstream Lambdas (`validate-file`, `extract-manifest`) receive a raw S3 key as `userId`. If H1 is fixed in Step Functions input, this resolves automatically.

- [ ] **M2 — Presigned URL expiry (1 hour) conflicts with CLAUDE.md guideline (5 min max)**
  - `src/lambda/core/presigned-url-export/index.py:14` and `lib/stack/lambda/index.ts:125`
  - The design doc justifies 1 hour for large file uploads on slow connections. CLAUDE.md states "5 min max". This conflict should be explicitly acknowledged in the design doc and the CLAUDE.md should be updated to reflect the approved exception.
  - Remediation: Document the exception in `design.md` and update CLAUDE.md.

- [ ] **M3 — CORS `allowedOrigins: ['*']` on exports bucket**
  - `lib/stack/s3/index.ts:52-56`
  - Any website can initiate a cross-origin PUT request using a valid presigned URL. In production, this should be scoped to the frontend domain.
  - Remediation: Replace `'*'` with the specific frontend origin (e.g. `https://app.healthnova.io`). Acceptable for dev.

- [ ] **M4 — Glue job timeout (8h) exceeds state machine timeout (4h)**
  - `lib/stack/glue/index.ts:71` (`timeout: 480`) vs `lib/stack/step-functions/index.ts:130` (`Duration.hours(4)`)
  - If the Glue job runs past the 4-hour state machine limit, the execution times out and transitions to `FAILED`, but the Glue job continues consuming DPUs for up to 4 additional hours. This creates orphaned Glue jobs and unexpected cost.
  - Remediation: Set the Glue job `timeout` to ≤ 240 minutes (4 hours) to match the state machine. Alternatively, add a Glue job cancellation step in the state machine's `TimeoutSeconds` catch block.

- [ ] **M5 — `log_lambda_event` utility logs full event payload (latent PHI risk)**
  - `src/layer/python-common/python/common/logger.py:52`
  - This function calls `json.dumps(event, default=str)` and logs it at INFO level. It is currently called by `post-confirmation-signup` and `process` Lambdas (which may receive email addresses or user attributes), and could be inadvertently added to ingestion Lambdas in the future.
  - Remediation: Remove or guard this function — either delete it, replace with a safe metadata-only version, or add a docstring warning against using it with PHI-carrying events.

### LOW

- [ ] **L1 — DynamoDB tables use AWS-managed encryption (not CMK)**
  - All three DynamoDB tables use the default AWS-managed key (`aws/dynamodb`). For a HIPAA-covered entity, customer-managed KMS keys (CMK) are strongly recommended to satisfy the HIPAA Security Rule's encryption and key management requirements.
  - Remediation: Add `encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED` and a dedicated KMS key in the `DynamoConstruct`.

- [ ] **L2 — No DynamoDB TTL on health-records table**
  - Health records are retained indefinitely. Without TTL, user data cannot be automatically purged per a data retention policy.
  - Remediation: Add a `ttl` attribute and configure TTL in the table definition. Deferred to future data retention policy change per design doc.

- [ ] **L3 — Glue continuous logging not explicitly disabled**
  - The design doc states "disable Glue continuous logging for data content" to prevent PHI leakage. The CDK Glue job definition (`lib/stack/glue/index.ts`) does not explicitly disable it via `--enable-continuous-cloudwatch-log: false`.
  - Remediation: Add `'--enable-continuous-cloudwatch-log': 'false'` to `defaultArguments`.

- [ ] **L4 — `sourceName` from Apple Health XML stored in DynamoDB**
  - `src/glue/parse_health_xml.py:123` stores `sourceName` (e.g. "iPhone", "Apple Watch Series 8 (John's Watch)"). Device names can contain the user's full name and may be considered quasi-identifying data under HIPAA.
  - Remediation: Evaluate whether `sourceName` is needed for analytics. If not, remove it from the stored item.

---

## HIPAA Compliance Checklist

- [x] Encryption at rest — S3 SSE-S3, DynamoDB AWS-managed key
- [x] Encryption in transit — `enforceSSL: true` on exports bucket; API Gateway HTTPS only
- [x] No PHI in ingestion Lambda logs — all log statements use record counts, statuses, and durations only
- [x] No PHI in Glue logs — only counts and progress logged; `sourceName` stored in DDB but not logged
- [x] Presigned URL scoped to user prefix via IAM condition (`exports/*`)
- [x] Cognito JWT required for presigned URL endpoint
- [x] Step Functions execution history retains audit trail (90 days, per design decision)
- [x] S3 versioning enabled on exports bucket
- [x] S3 lifecycle policy — Glacier after 90 days
- [ ] Customer-managed KMS keys for DynamoDB (LOW — L1)
- [ ] PHI-safe `log_lambda_event` utility (MEDIUM — M5)
- [ ] Wildcard IAM policies removed (CRITICAL — C1)

---

## IAM Policy Review

| Lambda | Policy | Scope | Status |
|--------|--------|-------|--------|
| `presigned-url-export` | `s3:PutObject` on `exports/*` | Scoped ✓ | OK |
| `validate-file` | `s3:GetObject`, `s3:HeadObject` on `exports/*` | Scoped ✓ | OK |
| `extract-manifest` | `s3:GetObject`, `s3:HeadObject` on `exports/*` | Scoped ✓ | OK |
| `mark-complete` | `dynamodb:PutItem`, `dynamodb:BatchWriteItem` on health-records table | Scoped ✓ | OK |
| `parse-ecg` | S3 read + DDB write, both scoped | Scoped ✓ | OK |
| `parse-gpx` | S3 read + DDB write, both scoped | Scoped ✓ | OK |
| `presigned-url-upload` | `s3:*` on `*` (via shared `s3Policy`) | **Wildcard ✗** | CRITICAL |
| `post-confirmation-signup` | `dynamodb:*` on `*` (via shared `dynamoPolicy`) | **Wildcard ✗** | CRITICAL |
| `process` | `dynamodb:*` on `*` (via shared `dynamoPolicy`) | **Wildcard ✗** | CRITICAL |
| Glue `parse-health-xml` | `s3:GetObject` on `exports/*`, DDB write on health-records | Scoped ✓ | OK |
| Glue role | `AWSGlueServiceRole` managed policy + scoped additions | Acceptable ✓ | OK |

---

## Recommendations

1. **[C1 — MUST FIX]** Replace `s3Policy` and `dynamoPolicy` shared wildcards with scoped `PolicyStatement`s per Lambda. This is the most impactful security improvement and should be a prerequisite for production deployment.

2. **[H1 — MUST FIX]** Fix the EventBridge → Step Functions input mapping to extract `userId` from the S3 key path. Example approach:
   ```typescript
   // In rule.addTarget input:
   userId: events.EventField.fromPath('$.detail.object.key')
   // Must be post-processed — add a Lambda step before ValidateFile
   // that splits the key: "exports/{userId}/{timestamp}.zip" → userId
   ```

3. **[H2 — MUST FIX before processing large files]** Refactor `validate-file` and `extract-manifest` to use S3 byte-range requests for the ZIP central directory instead of loading the entire object body.

4. **[H3 — MUST FIX before production]** Remove public access from the photos bucket.

5. **[M4 — SHOULD FIX]** Align Glue job timeout with state machine timeout (both ≤ 4 hours).

6. **[M5 — SHOULD FIX]** Deprecate `log_lambda_event` or add a guard against PHI-carrying events.

7. **[L3 — QUICK WIN]** Add `'--enable-continuous-cloudwatch-log': 'false'` to Glue job `defaultArguments`.

---

## Approved for Production

- [ ] All CRITICAL issues resolved (C1 — wildcard IAM policies)
- [ ] All HIGH issues resolved or formally accepted (H1 — userId mapping, H2 — memory OOM, H3 — public photos bucket)
- [ ] HIPAA compliance verified with customer-managed KMS keys (L1)
- [ ] `log_lambda_event` PHI risk addressed (M5)
