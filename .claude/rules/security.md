---
paths:
  - "lib/**/*.ts"
  - "src/lambda/**/*.py"
  - "src/layer/**/*.py"
---

# Security Rules

- Encrypt all data at rest and in transit
- Use least privilege IAM policies. Never use `*` in Actions unless absolutely necessary and scoped to specific resources.
- Time-limited presigned URLs (1 hour max)
- No hardcoded credentials
- HIPAA-aware logging (no PHI)
