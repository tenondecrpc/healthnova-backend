# Security — Pending Options

Status of AWS security services and tools for this project.

## Implemented

| Service | What it does | Est. cost/month |
|---|---|---|
| **GuardDuty** | Threat detection: unusual API calls, suspicious IPs, S3/Lambda anomalies | ~$4–$30 |
| **CloudTrail** | Audit log of all API calls in the account (who, what, when, from where) | ~$2 |
| **IAM Access Analyzer** | Detects publicly exposed resources (S3 buckets, IAM roles, etc.) | Free |
| **WAF v2** | Protects API Gateway: blocks SQLi, XSS, bad inputs, rate limits per IP | ~$5 + $0.60/M requests |
| **Gitleaks (CI)** | Scans PR commits for leaked secrets (AWS keys, passwords, tokens) | Free |
| **Checkov (CI)** | Static analysis on CDK/CloudFormation for IaC misconfigurations | Free |
| **Claude Security Review (CI)** | AI-based security review on PRs | API cost only |
| **AWS Budgets** | Cost alerts at 80% and 100% of monthly budget | Free |
| **S3 Block Public Access** | All buckets block public access by default | Free |
| **S3 SSL enforcement** | Denies non-HTTPS connections to health exports bucket | Free |
| **Cognito password policy** | Min 8 chars, uppercase, lowercase, digits | Free |
| **API Gateway throttling** | Rate limiting per stage (200 burst dev, 500 burst prod) | Free |
| **GitHub OIDC** | Keyless auth for GitHub Actions — no long-lived AWS credentials in secrets | Free |

## Not implemented — Worth considering

### Gitleaks pre-commit hook (local)

**What**: Blocks commits with secrets before they reach GitHub.

**Why not yet**: The CI pipeline already catches leaks on PRs. If a secret reaches GitHub, a force push removing the commit is viable since the repo is private with no collaborators.

**When to add**: If collaborators join the project.

```bash
brew install gitleaks
echo 'gitleaks protect --staged -v' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### AWS Secrets Manager

**What**: Stores and auto-rotates credentials (DB passwords, API keys, third-party tokens).

**Est. cost**: ~$0.40/secret/month + $0.05/10K API calls.

**Why not yet**: No third-party integrations or database credentials to manage. Lambda env vars with Cognito tokens are sufficient for now.

**When to add**: When integrating external health APIs or adding RDS/Aurora.

### AWS Security Hub

**What**: Centralized dashboard that aggregates findings from GuardDuty, IAM Access Analyzer, Config, Inspector. Runs automated compliance checks (CIS Benchmarks, AWS Foundational Security Best Practices).

**Est. cost**: ~$5–$15/month (based on number of findings and checks).

**Why not yet**: Overhead for a single-developer project. Individual services (GuardDuty, Access Analyzer) already send findings to CloudWatch/console.

**When to add**: Before going to production with real users, or if the number of AWS services grows significantly.

### AWS Config (rules)

**What**: Continuously evaluates resource configurations against rules (e.g., "all S3 buckets must be encrypted", "no security groups with 0.0.0.0/0 ingress").

**Est. cost**: ~$2–$10/month (per rule evaluation).

**Why not yet**: Checkov in CI catches IaC misconfigurations at deploy time. AWS Config catches drift after deploy — useful but redundant for a project without manual console changes.

**When to add**: If anyone starts making manual changes via AWS Console instead of CDK.

### GitHub Secret Scanning (native)

**What**: Same as Gitleaks but with push protection (blocks the push before secrets reach GitHub), auto-revocation with AWS, and 200+ provider patterns.

**Est. cost**: Free for public repos. $19/user/month (GitHub Advanced Security) for private repos.

**Why not yet**: $19/month for a single-developer private repo is hard to justify. Gitleaks covers AWS patterns. The 30-second exposure window on PRs is acceptable for a private repo with no collaborators.

**When to add**: If the repo goes public or the team grows.

### AWS Shield Advanced

**What**: Advanced DDoS protection with 24/7 response team, cost protection (AWS refunds attack-related cost spikes), and WAF rule recommendations.

**Est. cost**: $3,000/month.

**Why not yet**: Enterprise service. Shield Standard (free, already active) + WAF rate limiting covers the realistic threat model for a personal project.

**When to add**: Never, unless this becomes a commercial product with SLA requirements.

## Priority order if scaling

If this project moves beyond personal use:

1. **Secrets Manager** — as soon as external integrations or databases appear
2. **Gitleaks pre-commit hook** — as soon as collaborators join
3. **Security Hub** — before production launch with real users
4. **AWS Config** — if anyone uses the AWS Console directly
5. **GitHub Secret Scanning** — if repo goes public or team > 3 people
