---
paths:
  - "lib/**/*.ts"
  - "src/lambda/**/*.py"
  - "src/layer/**/*.py"
---

# Security Rules

- Encrypt all data at rest and in transit
- **IAM: Always use granular, scoped policies.** Every IAM policy (Lambda, Glue, OIDC, Step Functions, etc.) must specify concrete actions (`dynamodb:PutItem`, `s3:GetObject`, etc.) and specific resource ARNs. **Never** create shared policy files with wildcard actions (`service:*`) or wildcard resources (`Resource: *`). The `lib/stack/shared/policy/` directory was deleted for this reason — do not recreate it.
- Time-limited presigned URLs (1 hour max — exception for health exports due to file size, documented in design.md)
- No hardcoded credentials
- HIPAA-aware logging (no PHI in any log path — use `log_request_metadata`, never `log_lambda_event`)
