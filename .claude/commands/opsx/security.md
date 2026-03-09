---
name: /opsx:security
description: Run security review on an OpenSpec change
---

Perform a comprehensive security review of an OpenSpec change.

**Usage:**
```
/opsx:security [change-name]
```

If no change name is provided, the skill will prompt you to select from available changes.

**What it does:**
1. Analyzes the change for security vulnerabilities
2. Validates HIPAA compliance requirements
3. Reviews IAM policies and access controls
4. Checks for PHI/PII leakage in logs
5. Verifies encryption at rest and in transit
6. Generates a detailed security report

**When to use:**
- After completing implementation (`/opsx:apply`)
- Before archiving a change (`/opsx:archive`)
- When adding new AWS services or data flows
- After making security-related changes

**Output:**
- Security status (PASS/FAIL/WARNINGS)
- Findings by severity (CRITICAL/HIGH/MEDIUM/LOW)
- HIPAA compliance checklist
- Actionable recommendations
- Written report at `openspec/changes/<name>/security-review.md`

**Example workflow:**
```bash
/opsx:apply health-data-ingestion    # Implement
/opsx:security health-data-ingestion # Review security
# Fix any issues found
/opsx:security health-data-ingestion # Re-review
/opsx:archive health-data-ingestion  # Archive when PASS
```

**Invokes:** openspec-security-review skill

