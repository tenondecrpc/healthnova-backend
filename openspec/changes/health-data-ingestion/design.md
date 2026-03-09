## Context

HealthNova needs to ingest Apple Health export ZIP files (up to ~1GB) and transform them into queryable health records. The system must handle large XML files (exportar.xml can exceed 500MB), ECG CSV files, and GPX workout routes. The pipeline must be event-driven, scalable per user, and HIPAA-aware (no PHI in logs).

Current state: no upload or processing infrastructure exists. This is greenfield.

## Goals / Non-Goals

**Goals:**
- Authenticated presigned URL generation for direct browser-to-S3 uploads
- Async Step Functions workflow triggered by S3 upload events
- Scalable XML parsing via AWS Glue for large exports (no timeout, auto-scales DPUs)
- Normalize and persist health records to DynamoDB for downstream analytics
- Parse ECG CSVs and GPX workout routes in parallel Lambda branches
- Per-step error handling, retries, and observability via Step Functions execution history
- HIPAA-aware logging (no PHI/PII in CloudWatch or Glue logs)

**Non-Goals:**
- Real-time analytics or risk scoring (future change)
- Multi-file or incremental exports (full export.zip only)
- Export deduplication across uploads (future)
- Frontend upload UI (API contract only)

## Decisions

### 1. Direct S3 upload via presigned URL (not through API Gateway)

Apple Health exports can be 500MB–1GB. Routing through API Gateway and Lambda would hit the 6MB payload limit. Presigned URLs let the browser upload directly to S3, keeping the backend stateless.

**Presigned URL Lambda** is the only Lambda in the hot path — lightweight, sub-100ms, remains suitable for Lambda.

**Alternatives considered:**
- Multipart upload via backend proxy — rejected (complexity, payload limits)

### 2. Step Functions Standard Workflow as the processing orchestrator

Step Functions provides per-step retries, granular error handling, full execution history for debugging, and native integrations with Lambda, Glue, and ECS. Each upload triggers one execution with a complete audit trail.

**Processing flow:**
```
S3 ObjectCreated → EventBridge → Step Functions execution
                                        │
                              [Validate & classify file]
                              (Lambda — size check, ZIP integrity)
                                        │
                              [Extract manifest]
                              (Lambda — list files inside ZIP)
                                        │
                    ┌───────────────────┴──────────────────────┐
                    ▼                                          ▼
         [Parse exportar.xml]                      [Parallel branch]
         (Glue Job — stream XML,                    ├─ Parse ECG CSVs (Lambda)
          batch write to DDB)                       └─ Parse GPX routes (Lambda)
                    │                                          │
                    └──────────────────────────────────────────┘
                                        │
                              [Mark upload complete]
                              (Lambda — update DDB job status)
```

**Why Standard Workflow (not Express):**
- Execution history persisted for 90 days — critical for debugging health data issues
- Supports native `.sync:2` integrations for waiting on Glue jobs
- Processing is not high-frequency (no need for Express Workflow's 100k/s throughput)

**Alternatives considered:**
- Lambda-only pipeline — rejected (15-min timeout unsuitable for large XML files)
- Fargate for XML parsing — considered but Glue is serverless, auto-scales DPUs, and has no timeout limit (up to 48h); better fit for arbitrarily large ETL workloads
- SQS + Fargate without orchestration — rejected (no per-step visibility, harder error handling)

### 3. AWS Glue job for exportar.xml parsing

`exportar.xml` regularly exceeds 500MB. AWS Glue is a fully serverless ETL service with:
- No execution timeout cap (up to 48 hours)
- Auto-scaling worker DPUs based on data size
- Native S3 streaming — reads the file without full local download
- Built-in job bookmarks and retry support

The Glue job uses Python Shell (not Spark) since the XML parsing is sequential by nature. It reads the ZIP from S3 as a streaming byte range, feeds the XML to `iterparse`, and uses `batch_write_item` to persist records to DynamoDB.

Step Functions uses the `.sync:2` Glue integration to start the job and wait for completion natively.

**Alternatives considered:**
- Lambda — rejected (15-min timeout, 10GB /tmp)
- Fargate — valid for general containers but Glue avoids container management, has better ETL observability (Glue job runs, metrics), and scales DPUs automatically
- Distributed Map over XML chunks — rejected (splitting XML mid-stream is fragile)

### 4. Lambda for ECG CSV and GPX parsing

ECG CSV files and GPX workout routes are individually small (KB–low MB). Lambda is well-suited — fast, no container management, runs in parallel via Step Functions `Parallel` state.

### 5. Single DynamoDB table with composite key design

`PK = USER#{user_id}`, `SK = RECORD#{type}#{timestamp}`. Supports queries by user, record type, and time range via a single GSI. On-demand capacity to handle burst writes from batch inserts.

**Alternatives considered:**
- Separate tables per record type — rejected (cross-type queries harder, operational overhead)
- Timestream — rejected (additional cost and service dependency for MVP)

### 6. EventBridge rule between S3 and Step Functions

EventBridge decouples S3 from the workflow and allows adding other consumers (e.g., audit logging) without changing S3 bucket config. Filtering ensures only `.zip` uploads to the `exports/` prefix trigger the workflow.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Glue job startup latency (~30–60s cold start) | Acceptable for async processing; users are not waiting synchronously |
| Glue DPU cost for small exports | Use Python Shell (0.0625 DPU) for sequential XML parsing — minimal cost for files under 200MB |
| DynamoDB write throttling during batch inserts | `batch_write_item` with exponential backoff; on-demand capacity mode |
| S3 presigned URL replay | 1-hour expiry; URL scoped to `{user_id}/` prefix via IAM condition |
| ZIP bomb / malformed export | Validate file size and structure in the Validate Lambda before starting the Glue job |
| PHI leakage in logs | Log only record counts, types, durations — never field values; disable Glue continuous logging for data content |
| Step Functions execution timeout | Set max execution duration to 4 hours; alert via CloudWatch alarm if exceeded |

## Migration Plan

1. Deploy CDK stack: S3 bucket, EventBridge rule, Step Functions state machine, Glue job + script (Python Shell), DynamoDB table, Lambda functions, API Gateway
2. No data migration required (greenfield)
3. Rollback: disable EventBridge rule to stop new executions; in-flight Glue jobs can be cancelled via console or API

## Open Questions

- Should we retain the raw export.zip after processing? (Current plan: Glacier after 90 days)
- What DynamoDB TTL for health records? (Deferred to data retention policy change)
- Should we add a file size threshold to choose between Python Shell (small) and Spark (very large) Glue worker type?
