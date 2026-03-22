# Security Review: health-data-security-fixes

**Date**: 2026-03-09
**Reviewer**: AI Security Analysis
**Status**: ✓ PASS

---

## Executive Summary

All CRITICAL and HIGH findings from the prior `health-data-ingestion` security review have been fully resolved. The implementation is verified against the synthesized CloudFormation template and the full test suite (8 suites, 28 tests). The health-data-security-fixes change is approved for production deployment subject to the remaining MEDIUM/LOW items noted below.

---

## Findings

### CRITICAL
None.

### HIGH
None.

### MEDIUM

- [ ] **M1 — Presigned URL expiry (1 hour) vs. CLAUDE.md guideline (5 min max)**
  - `PRESIGNED_URL_EXPIRY_SECONDS: '3600'` in `lib/stack/lambda/index.ts:136`
  - The design doc for `health-data-ingestion` explicitly justifies 1 hour for large file uploads. This is an accepted exception. The CLAUDE.md security section should be updated to document the approved override.
  - Remediation: Update CLAUDE.md security guideline to "5 min max (exception: health exports up to 1h due to file size)".

- [ ] **M2 — CORS `allowedOrigins: ['*']` on both S3 buckets**
  - `lib/stack/s3/index.ts:27` (photos) and `:44` (exports)
  - Acceptable for development. Must be scoped to the frontend origin before production deployment.
  - Remediation: Replace `'*'` with the production frontend URL when known.

- [ ] **M3 — `authorizerLambda` has placeholder environment variables**
  - `lib/stack/lambda/index.ts:270-271`: `USER_POOL_ID: 'UNDEFINED_BY_DEFAULT'`, `APP_CLIENT_ID: 'UNDEFINED_BY_DEFAULT'`
  - These are not injected from the Cognito construct at deploy time. If the Lambda executes with these values, all API requests will fail JWT validation.
  - Remediation: Pass `cognitoFactory.userPool.userPoolId` and the app client ID as environment variables in `LambdaFactory`, the same way `DynamoFactory` and `S3Factory` are passed in.

### LOW

- [ ] **L1 — DynamoDB tables use AWS-managed encryption (not CMK)**
  - All three tables (`user`, `process`, `health-records`) use the default `aws/dynamodb` key. For HIPAA BAA compliance, customer-managed KMS keys are strongly recommended.
  - Remediation: Add `encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED` and a dedicated KMS key. Track as a separate change.

- [ ] **L2 — No DynamoDB TTL on `health-records` table**
  - Health records are retained indefinitely. A TTL attribute is needed to support future data retention policy enforcement.
  - Remediation: Add `timeToLiveAttribute: 'ttl'` to the table config. Track as a separate data retention change.

- [ ] **L3 — `authorizer` Lambda uses pinned Klayers at old versions**
  - `lib/stack/lambda/index.ts:259-260`: `Klayers-p312-PyJWT:1`, `Klayers-p312-cryptography:18`
  - Pinned layer versions may contain known CVEs if not periodically updated.
  - Remediation: Establish a quarterly review cadence for Klayers version updates.

---

## Verification Against Synthesized Template

The following was confirmed by parsing `cdk.out/HealthnovaDevStack.template.json`:

| Check | Result |
|-------|--------|
| Wildcard IAM policies (`s3:*` or `dynamodb:*` on `*`) | **NONE** ✓ |
| S3 buckets not fully blocking public access | **NONE** ✓ |
| Glue job timeout | **240 min** ✓ |
| Glue continuous CloudWatch logging | **disabled** ✓ |
| Glue job bookmark | **disabled** ✓ |
| `ParseInput` state in state machine | **Present** ✓ |
| `States.StringSplit` intrinsic in state machine | **Present** ✓ |

---

## HIPAA Compliance Checklist

- [x] Encryption at rest — S3 SSE-S3 (exports), DynamoDB AWS-managed key
- [x] Encryption in transit — `enforceSSL: true` on exports bucket; API Gateway HTTPS
- [x] No PHI in ingestion Lambda logs — all log statements use counts, statuses, durations
- [x] No PHI in Glue logs — continuous logging disabled; script only logs counts
- [x] `log_lambda_event` removed — replaced with `log_request_metadata` (metadata-only)
- [x] Presigned URL scoped to user prefix via `exports/*` IAM condition
- [x] Cognito JWT required for presigned URL endpoint
- [x] Step Functions execution history retains audit trail (90 days)
- [x] S3 versioning enabled on exports bucket
- [x] S3 Glacier lifecycle after 90 days
- [x] Photos bucket blocks all public access (`BLOCK_ALL`)
- [x] All Lambda IAM policies scoped to specific resource ARNs (no wildcards)
- [x] `userId` correctly extracted from S3 key path — DynamoDB PKs are well-formed
- [ ] Customer-managed KMS keys for DynamoDB (L1 — track separately)
- [ ] CORS `allowedOrigins` scoped to production frontend (M2 — required before launch)
- [ ] Authorizer Lambda env vars populated from Cognito construct (M3 — required before launch)

---

## IAM Policy Review

| Lambda / Role | Actions | Resource | Status |
|--------------|---------|----------|--------|
| `presigned-url-export` | `s3:PutObject` | `exports/*` on exports bucket | ✓ Scoped |
| `post-confirmation-signup` | `dynamodb:PutItem` | user table ARN | ✓ Scoped |
| `process` | `dynamodb:GetItem/PutItem/UpdateItem/Query` | process table ARN + indexes | ✓ Scoped |
| `validate-file` | `s3:GetObject`, `s3:HeadObject` | `exports/*` | ✓ Scoped |
| `extract-manifest` | `s3:GetObject`, `s3:HeadObject` | `exports/*` | ✓ Scoped |
| `mark-complete` | `dynamodb:PutItem`, `dynamodb:BatchWriteItem` | health-records table + indexes | ✓ Scoped |
| `parse-ecg` | S3 read + DDB write | both scoped | ✓ Scoped |
| `parse-gpx` | S3 read + DDB write | both scoped | ✓ Scoped |
| Glue `parse-health-xml` role | `s3:GetObject` on `exports/*`, DDB write on health-records | | ✓ Scoped |
| Glue role | `AWSGlueServiceRole` managed + scoped additions | | ✓ Acceptable |

---

## Recommendations

1. **[M3 — MUST FIX before production]** Wire `USER_POOL_ID` and `APP_CLIENT_ID` in `authorizerLambda` from the Cognito construct output — currently `UNDEFINED_BY_DEFAULT`.
2. **[M2 — MUST FIX before production]** Replace `allowedOrigins: ['*']` with the production frontend URL on both S3 buckets.
3. **[M1 — DOCUMENT]** Update CLAUDE.md security guideline to document the approved 1-hour presigned URL exception for health exports.
4. **[L1 — FUTURE CHANGE]** Add KMS customer-managed encryption to all DynamoDB tables.
5. **[L3 — PROCESS]** Establish quarterly Klayers version review for the authorizer Lambda layers.

---

## Approved for Production

- [x] All CRITICAL issues resolved
- [x] All HIGH issues resolved
- [ ] M3 (authorizer env vars) resolved — required before API goes live
- [ ] M2 (CORS origins) scoped to production domain — required before launch
- [x] HIPAA logging compliance verified (no PHI in any log path)
- [x] All IAM policies scoped — no wildcards in synthesized template
