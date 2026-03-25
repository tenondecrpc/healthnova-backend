# Post-Mortem: DynamoDB Cost Overrun — March 2026

## Incident Summary

| Field | Detail |
|-------|--------|
| **Date detected** | 2026-03-24 |
| **Duration** | 2026-03-18 to 2026-03-24 (6 days) |
| **Total cost incurred** | $1,155.66 (DynamoDB only) |
| **Total bill with tax** | $1,426.33 |
| **Expected monthly budget** | $100 (all AWS services) |
| **Root cause** | Provisioned DynamoDB capacity scaled up and never scaled back down |
| **Financial resolution** | AWS Support credited the accidental charges after a support case was filed explaining the incident |

## What Happened

The health data ingestion pipeline used **provisioned capacity** on the `health-records` DynamoDB table. Before each ingestion, a Step Functions workflow invoked a `ScaleDynamo` Lambda to scale Write Capacity Units (WCU) from 5 to 10,000 on both the table and its Global Secondary Index (GSI). After ingestion, the same Lambda was invoked to scale back down.

On March 18, the scale-down operation failed silently. The table remained at 10,000 WCU for 6 consecutive days, accumulating $312/day.

### Cost Timeline

| Date | DynamoDB Cost | Cumulative |
|------|--------------|------------|
| Mar 18 | $4.45 | $4.45 |
| Mar 19 | $62.99 | $67.44 |
| Mar 20 | $152.00 | $219.44 |
| Mar 21 | $312.00 | $531.44 |
| Mar 22 | $312.00 | $843.44 |
| Mar 23 | $312.21 | $1,155.65 |

### Cost Breakdown ($312/day)

```
Table:  10,000 WCU x $0.00065/WCU/hr x 24h = $156.00/day
GSI:    10,000 WCU x $0.00065/WCU/hr x 24h = $156.00/day
Total:                                        $312.00/day
```

## Root Causes

### 1. Silent failure on scale-down

The `ScaleDynamo` Lambda caught and swallowed exceptions during scale-down, returning success to Step Functions:

```python
except Exception as e:
    if action != "down":
        raise
    logger.warning("ScaleDynamoDown failed, skipping: %s", e)
    return {"scaled": False, "skipped": True, "wcu": wcu}
```

The workflow continued to `MarkComplete` without error, so no alarm fired.

### 2. Aggressive default WCU

The Lambda defaulted to `WCU_HIGH = 10,000` if the environment variable was missing, higher than the intended 7,000 configured in CDK.

### 3. Unused GSI doubling write costs

The `UserTypeIndex` GSI had the same partition key (`PK`) as the base table. No dashboard query ever used this index, yet it doubled all write capacity costs.

### 4. No working cost alerts

Multiple layers of alerting failed simultaneously:

- **Budget Alerts (email not confirmed):** AWS Budgets was configured, but the email subscription was never confirmed. AWS Budget email notifications require the subscriber to click a confirmation link. Since this was missed, no budget alert was ever delivered — not at 80%, not at 100%, not the forecast alert. The entire alerting layer was silently inoperative.
- **Cost Anomaly Detection (no monitor attached):** The `CfnAnomalySubscription` was deployed with `monitorArnList: []` — no anomaly monitor was connected. The subscription existed but had nothing to detect anomalies from.
- **SNS Topic (unused):** An SNS topic for budget alerts was created but never wired to any budget notification. It sat idle as a backup channel that could have worked if configured.
- **No daily budget:** Only a monthly budget existed. Even if email had been confirmed, the first alert would have fired at $80 (80% of $100), by which point 6+ days at $312/day would have already accumulated $1,155.

## Financial Resolution

A support case was filed with AWS explaining that the cost overrun was accidental — caused by an infrastructure bug that left provisioned DynamoDB capacity at 10,000 WCU for 6 days on a personal project with a $100/month budget. AWS Support reviewed the case and credited the accidental charges.

**Lesson:** AWS Support can issue one-time credits for accidental spending on personal/dev accounts when the cause is clearly a misconfiguration and not normal usage. File the case promptly with evidence (CloudWatch metrics, CloudTrail logs, cost timeline) showing the anomaly was unintentional.

## Resolution

### Changes Applied (branch: `fix/cors`)

| Change | File(s) | Impact |
|--------|---------|--------|
| Switch to `PAY_PER_REQUEST` billing | `lib/stack/dynamo/index.ts` | Eliminates provisioned capacity risk entirely |
| Remove `ScaleDynamo` Lambda | `src/lambda/ingestion/scale-dynamo/` (deleted), `lib/stack/lambda/index.ts`, `lib/stack/step-functions/index.ts` | Removes the component that caused the incident |
| Remove unused GSI `UserTypeIndex` | `lib/stack/dynamo/index.ts`, all ingestion Lambdas, Glue job | Halves per-item write cost |
| Remove `GSI1SK` attribute writes | `src/glue/parse_health_xml.py`, `src/lambda/ingestion/mark-complete/index.py`, `parse-ecg/index.py`, `parse-gpx/index.py` | Reduces item size and eliminates dead attribute |
| Fix Infracost workflow | `.github/workflows/cost-estimate.yml` | Points to specific CloudFormation `.template.json` instead of directory |
| Add daily budget alert ($10/day) | `lib/construct/budget-construct.ts` | Catches daily spending spikes within 24 hours |
| Fix Cost Anomaly Detection | `lib/construct/budget-construct.ts` | Created `DIMENSIONAL/SERVICE` monitor and linked to subscription |
| Wire SNS topic to all budget notifications | `lib/construct/budget-construct.ts` | Backup delivery channel if email subscription is missed |
| Add 50% monthly budget threshold | `lib/construct/budget-construct.ts` | Earlier warning before hitting 80%/100% |

### Simplified Step Functions Workflow

**Before:**
```
ParseInput → ValidateFile → ExtractManifest → ScaleDynamoUp → ParallelParsing → ScaleDynamoDown → MarkComplete
                                                                    ↓ (on error)
                                                          ScaleDynamoDownOnError → MarkFailed
```

**After:**
```
ParseInput → ValidateFile → ExtractManifest → ParallelParsing → MarkComplete
                                                    ↓ (on error)
                                                  MarkFailed
```

### Cost Comparison (1 ingestion/month, 2M records)

| | Before (provisioned, working correctly) | Before (stuck at 10K WCU) | After (on-demand) |
|---|---|---|---|
| DynamoDB writes | ~$5.00 | $150.00+/day | $2.50 |
| DynamoDB base capacity | ~$100.00 (100 RCU × 2) | $312.00/day | $0.00 |
| GSI overhead | 2x write cost | 2x write cost | None |
| **Monthly total** | ~$120 | ~$9,360 | **~$12.50** |

## Preventive Measures

### 1. Never use provisioned capacity for bursty workloads

On-demand billing is the correct choice when:
- Writes are infrequent and bursty (monthly ingestion)
- Reads are light (dashboard queries)
- The cost of a capacity management bug exceeds the savings from provisioned pricing

**Rule: Use provisioned capacity only when sustained throughput is predictable AND the savings justify the operational risk.**

### 2. Never silently swallow infrastructure failures

If a scale-down, cleanup, or teardown operation fails, the workflow **must** fail visibly. Silent failures create invisible cost leaks that can run for days before detection.

### 3. Validate Infracost shows real numbers before merging infrastructure changes

The Infracost PR comment was showing "No cloud resources detected" because it scanned a directory instead of the specific CloudFormation template file. Cost estimation tooling must be validated to produce real output before relying on it as a gate.

### 4. Audit GSIs for actual usage

Every GSI doubles write costs and adds storage. Before deploying a GSI, verify that at least one query path requires it. Periodically audit existing GSIs against actual query patterns — if `CloudWatch Contributor Insights` shows zero reads on a GSI, remove it.

## Multi-Layer Cost Control Strategy

A single alerting mechanism is a single point of failure. This incident proved that when the email subscription wasn't confirmed, **all** visibility was lost. The following multi-layer strategy ensures that no single failure can leave cost spikes undetected.

### Layer 1: Daily Budget Alert (automated, immediate)

A `DAILY` AWS Budget with a $10/day limit fires at 80% ($8) and 100% ($10). This is the fastest automated alert — would have caught the $312/day spike within the first day.

**Configured in:** `lib/construct/budget-construct.ts`

### Layer 2: Monthly Budget with early thresholds (automated)

Monthly budget alerts at 50%, 80%, and 100% actual spend, plus 100% forecasted. The 50% threshold provides an early signal mid-month.

**Configured in:** `lib/construct/budget-construct.ts`

### Layer 3: Cost Anomaly Detection (automated, ML-based)

AWS Cost Anomaly Detection uses ML to learn spending patterns per service and alerts when actual spend deviates from the expected baseline. A `DIMENSIONAL/SERVICE` monitor detects per-service anomalies (e.g., DynamoDB spike) with a $10 minimum impact threshold.

**Configured in:** `lib/construct/budget-construct.ts`

### Layer 4: SNS Topic as backup delivery — Email + SMS (redundancy)

All budget notifications and anomaly alerts are sent to both direct email AND an SNS topic. If the email subscription is not confirmed or email delivery fails, the SNS topic still receives the notification. This allows:
- Adding a second email later without redeploying
- Subscribing a Slack webhook or Lambda for custom routing
- Reviewing missed alerts via CloudWatch Logs if an SNS delivery Lambda is attached

**SMS alerts** are also supported. Phone numbers configured via `BUDGET_ALERT_PHONES` env var (E.164 format, e.g., `+5491112345678`) are subscribed to the same SNS topic and receive the same alerts as email.

**Configured in:** `lib/construct/budget-construct.ts`, `bin/main.ts`

#### SMS Sandbox Setup (required for new AWS accounts)

New AWS accounts are in **SNS SMS Sandbox** by default. In sandbox mode, SMS can only be sent to verified phone numbers. This is sufficient for personal alerting (1-2 numbers).

**To verify your phone number:**

1. AWS Console → SNS → Text messaging (SMS) → Sandbox destination phone numbers
2. Click "Add phone number" → enter number in E.164 format (e.g., `+5491112345678`)
3. Receive a verification code via SMS → enter it in the console
4. Done — your number now receives all SNS SMS alerts

**To exit SMS Sandbox (optional, only needed for multiple unverified recipients):**

1. AWS Console → SNS → Text messaging (SMS) → Exit SMS sandbox
2. Fill the form: message type = **Transactional**, estimated monthly spend, use case description ("cost alerting for infrastructure budget")
3. AWS reviews and responds in **1-2 business days**
4. Once approved, SMS can be sent to any phone number without prior verification

For this project (single recipient for budget alerts), staying in sandbox mode and verifying the phone number is the simplest and recommended approach.

### Layer 5: Infracost PR diff (pre-deploy, human review)

Every PR that touches `lib/**` or `bin/**` triggers an Infracost cost diff in the GitHub Actions workflow. The PR comment shows the estimated monthly cost change **before** merging, giving the reviewer a chance to catch expensive changes.

**Configured in:** `.github/workflows/cost-estimate.yml`

### Layer 6: Manual weekly cost review (human, 5 minutes)

No automated system replaces a quick manual check. Once per week:

1. Open **AWS Cost Explorer** → filter by `Project` tag → check last 7 days
2. Look for any day that exceeds $5 (normal daily cost is ~$0.40)
3. If a spike exists, check **DynamoDB → Tables → Metrics** for unexpected throughput

This 5-minute weekly habit acts as the final safety net when all automated layers fail — as they did in this incident. The first $4.45 spike on Mar 18 would have been visible in a manual check within the same week.

### Summary: Detection timeline for each layer

| Layer | Would have detected by | Days of exposure |
|-------|----------------------|------------------|
| Daily Budget ($10/day) | Mar 18 (day 1) | 0 |
| Cost Anomaly Detection | Mar 19 (day 2) | 1 |
| Monthly Budget (50%) | Mar 19 ($50 reached) | 1 |
| Infracost PR diff | Before deploy | 0 |
| Weekly manual review | Mar 24 (next check) | 6 |
| Monthly Budget (80%) | Mar 19 ($80 reached) | 1 |
| **What actually happened** | **Mar 24 (CSV review)** | **6** |
