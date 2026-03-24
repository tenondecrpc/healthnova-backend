---
paths:
  - "test/**/*.ts"
---

# Testing Standards

- **Shared Setup**: ALWAYS use the setup helper to get the CDK template `import { getTemplate } from '../helpers/setup';` to avoid instantiating the stack multiple times.
- **Files**: `test/[domain]/[resource].test.ts`
- **Important Rules**:
  1. Organize by AWS domain (S3, Lambda, DynamoDB, Step Functions).
  2. One file per main resource. Do not mix tests for different resources.
  3. Descriptive tests explaining what specific behavior is being verified.
- **What to test**: Resource configuration (properties, environment variables), and IAM Policies.
- **Do NOT include**: Lambda business logic tests (these go in Python unit tests), E2E tests, or tests that require actual AWS deployment.
