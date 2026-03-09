---
name: _openspec-security-review
description: Internal skill for security review. Use /opsx:security command instead.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: healthnova
  version: "1.0"
  internal: true
---

Perform a comprehensive security review of an OpenSpec change.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the **AskUserQuestion tool** to let the user select

   Always announce: "Security review for change: <name>"

2. **Get change context**

   ```bash
   openspec status --change "<name>" --json
   ```

   Read all relevant artifacts:
   - proposal.md
   - design.md
   - tasks.md
   - All spec files in specs/ directory

3. **Perform security analysis**

   Analyze the following security dimensions:

   **A. HIPAA Compliance**
   - ✓ Encryption at rest (S3, DynamoDB, EBS)
   - ✓ Encryption in transit (TLS/HTTPS)
   - ✓ No PHI/PII in logs (CloudWatch, Glue logs, Lambda logs)
   - ✓ Access controls and audit trails
   - ✓ Data retention and lifecycle policies

   **B. IAM & Access Control**
   - ✓ Least privilege principle applied
   - ✓ No wildcard resource ARNs (`*`)
   - ✓ Resource-level permissions with conditions
   - ✓ Cross-service access properly scoped
   - ✓ Lambda execution roles reviewed

   **C. Data Protection**
   - ✓ S3 bucket policies and ACLs
   - ✓ Presigned URL expiration and scope
   - ✓ DynamoDB encryption and access patterns
   - ✓ Secrets management (no hardcoded credentials)
   - ✓ Input validation and sanitization

   **D. Network Security**
   - ✓ API Gateway authorization (Cognito)
   - ✓ VPC configuration if applicable
   - ✓ Security groups and NACLs
   - ✓ Public vs private resources

   **E. Logging & Monitoring**
   - ✓ CloudWatch alarms for security events
   - ✓ CloudTrail enabled for audit
   - ✓ No sensitive data in logs
   - ✓ Error handling doesn't leak information

   **F. Code Security**
   - ✓ Dependency vulnerabilities
   - ✓ SQL injection prevention
   - ✓ Path traversal prevention
   - ✓ Proper error handling

4. **Scan implementation files**

   For each Lambda function and infrastructure file:
   - Check for hardcoded secrets or credentials
   - Verify IAM policy statements
   - Check logging statements for PHI leakage
   - Validate input sanitization
   - Review error handling

5. **Generate security report**

   Create a structured report with:
   - **Summary**: Overall security posture (PASS/FAIL/WARNINGS)
   - **Findings**: List of issues by severity (CRITICAL/HIGH/MEDIUM/LOW)
   - **Recommendations**: Actionable fixes for each finding
   - **Compliance**: HIPAA checklist status

6. **Save security report**

   Write report to: `openspec/changes/<name>/security-review.md`

   Format:
   ```markdown
   # Security Review: <change-name>
   
   **Date**: YYYY-MM-DD
   **Reviewer**: AI Security Analysis
   **Status**: PASS | FAIL | WARNINGS
   
   ## Executive Summary
   [Overall assessment]
   
   ## Findings
   
   ### CRITICAL
   - [ ] Finding 1
   - [ ] Finding 2
   
   ### HIGH
   - [ ] Finding 3
   
   ### MEDIUM
   - [ ] Finding 4
   
   ### LOW
   - [ ] Finding 5
   
   ## HIPAA Compliance Checklist
   - [x] Encryption at rest
   - [x] Encryption in transit
   - [ ] No PHI in logs (ISSUE FOUND)
   ...
   
   ## IAM Policy Review
   [Detailed analysis]
   
   ## Recommendations
   1. Fix critical issue X
   2. Address high priority Y
   ...
   
   ## Approved for Production
   - [ ] All CRITICAL issues resolved
   - [ ] All HIGH issues resolved or accepted
   - [ ] HIPAA compliance verified
   ```

7. **Display results**

   Show:
   - Security status (PASS/FAIL/WARNINGS)
   - Count of findings by severity
   - Critical issues that must be fixed
   - Link to full report

   **If CRITICAL or HIGH issues found:**
   - Block archive recommendation
   - Suggest fixing issues before archiving
   - Provide specific remediation steps

   **If only MEDIUM/LOW or PASS:**
   - Approve for archive
   - Note any minor improvements

**Output Format**

```
## Security Review Complete: <change-name>

**Status**: ⚠️ WARNINGS (or ✓ PASS or ❌ FAIL)

### Findings Summary
- CRITICAL: 0
- HIGH: 1
- MEDIUM: 2
- LOW: 3

### Critical Issues (Must Fix)
None

### High Priority Issues
1. Lambda function logs user_id which may be considered PII
   → Recommendation: Use hashed user identifiers in logs

### Report Location
openspec/changes/<name>/security-review.md

### Next Steps
- Review and address HIGH priority findings
- Update tasks.md with security fixes if needed
- Re-run security review after fixes
- Proceed to archive when PASS status achieved
```

**Guardrails**
- Always create a written security-review.md artifact
- Be thorough but practical - focus on real risks
- Provide actionable recommendations, not just problems
- Consider the HIPAA context of health data
- Don't block on minor issues, but flag critical ones
- Check actual implementation files, not just design docs
- Verify IAM policies in CDK code
- Scan for common security anti-patterns

**Integration with Archive Flow**

This skill should be run BEFORE `openspec-archive-change`:

```
/opsx:apply          # Implement tasks
/opsx:security       # Security review (NEW)
/opsx:archive        # Archive if security passes
```

