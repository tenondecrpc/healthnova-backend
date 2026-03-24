## Context

HealthNova has a complete ingestion pipeline that processes Apple Health exports and stores normalized records in DynamoDB. The `healthRecordsTable` uses 3 distinct PK patterns: sharded XML records (`USER#{id}#SHARD#{0-9}`), non-sharded ECG/GPX records (`USER#{id}`), and job status entries (`USER#{id}`). No read API exists. This change adds 5 dashboard endpoints to query this data.

Current API has 1 route (write): `POST /upload/presigned-url`.

## Goals / Non-Goals

**Goals:**
- Query health metrics with scatter-gather across 10 DynamoDB shards, with daily aggregation and raw paginated modes
- Query ECG and GPX records with cursor-based pagination
- Provide a composite summary endpoint for dashboard landing page
- Enforce date range limits (max 90 days) to prevent expensive queries
- Consistent error response format across all endpoints
- All queries scoped to authenticated user only

**Non-Goals:**
- Pre-computed aggregation tables (Phase 2 — DynamoDB Streams-based)
- New GSIs or table schema changes
- Real-time streaming / WebSocket updates
- Export or download functionality
- Cross-user analytics or admin endpoints

## Decisions

### 1. Scatter-gather pattern for sharded XML health records

XML health records are written with `PK = USER#{userId}#SHARD#{0-9}` (10 shards) for write throughput. To read them back, the Lambda fans out 10 parallel DynamoDB `Query` calls — one per shard — and merges results in memory.

```
Lambda receives request (type=HeartRate, start, end)
    │
    ├─► Query SHARD#0: PK=USER#abc#SHARD#0, SK between RECORD#HeartRate#start..end
    ├─► Query SHARD#1: PK=USER#abc#SHARD#1, SK between RECORD#HeartRate#start..end
    ├─► ...
    └─► Query SHARD#9: PK=USER#abc#SHARD#9, SK between RECORD#HeartRate#start..end
         │
         ▼
    Merge all results → sort by startDate → aggregate or paginate
```

**Why parallel, not sequential:** 10 sequential queries at ~10ms each = ~100ms. 10 parallel queries = ~15ms total. The fan-out adds code complexity but keeps p99 latency under 200ms for daily aggregation queries.

**Why this is acceptable for Phase 1:** For 90-day windows on HeartRate (~1440 readings/day × 90 = ~130k records), the in-memory aggregation is well within Lambda's memory limits (256MB+). Daily aggregation reduces the response to at most 90 data points.

**Alternatives considered:**
- New GSI with non-sharded PK — rejected (would require schema migration and Glue job changes; deferred to Phase 2 if scatter-gather proves costly)
- DynamoDB Streams to pre-aggregate — rejected for Phase 1 (additional infrastructure before measuring actual read patterns)

### 2. Cursor-based pagination for raw mode

For `granularity=raw`, the response includes a `nextCursor` token — a base64-encoded JSON object containing the `LastEvaluatedKey` per shard. This allows the client to resume queries across all 10 shards.

Shards that are exhausted are omitted from the cursor. When all shards are exhausted, `nextCursor` is `null`.

**Why not offset-based:** DynamoDB doesn't support offset pagination. `LastEvaluatedKey` is the native cursor. Encoding per-shard cursors into a single token preserves a simple client API.

### 3. On-demand aggregation in the summary endpoint (not pre-computed)

The `/dashboard/summary` endpoint runs up to 32 parallel DynamoDB queries (3 metric types × 10 shards + ECG count + GPX count) and aggregates in-memory.

**Why on-demand for Phase 1:**
- 7-day window keeps data volume manageable (~10k records per metric type)
- Avoid premature infrastructure (DynamoDB Streams, aggregation table, eventual consistency concerns)
- Measure actual usage patterns before optimizing

**When to move to pre-computed (Phase 2 triggers):**
- Summary endpoint p99 latency > 500ms
- DynamoDB read cost for summary exceeds $50/month
- Scaling beyond 1000 daily active users

### 4. Python Lambda functions with existing common layer

All 5 Lambda functions use Python (consistent with existing Lambdas) and the `python-common` layer for logging, CORS, and response formatting. DynamoDB access uses `boto3` resource API with `Table.query()`.

**Alternatives considered:**
- TypeScript Lambdas — rejected (all existing Lambda functions in the project are Python; mixing runtimes adds operational complexity)

### 5. Date range validation: max 90 days, required start/end

All metric endpoints require explicit `start` and `end` query parameters (ISO date format). The range cannot exceed 90 days. This prevents unbounded scatter-gather queries, accidental DynamoDB cost spikes, and Lambda timeouts on large result sets.

Raw mode is additionally capped at 1000 records per response.

### 6. ECG and GPX use direct queries (no scatter-gather)

ECG and GPX records use `PK = USER#{userId}` (non-sharded), so a single DynamoDB `Query` suffices. These endpoints are simpler and faster than the metrics endpoint.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Scatter-gather latency for 10 shards | Parallel queries keep p99 < 200ms; 90-day cap limits data volume |
| Summary endpoint cost (32 queries per call) | 7-day window keeps it bounded; monitor and move to pre-computed if cost > $50/month |
| Multi-shard cursor pagination complexity | Cursor encodes per-shard state; exhausted shards are dropped from cursor |
| Memory pressure on large raw queries | 1000 record limit per response; Lambda memory set to 256MB |
| PHI exposure in API responses | Health record values are returned (this is the purpose of the API); ensure HTTPS only, Cognito auth enforced, no logging of response bodies |
| Clock skew in date filtering | SK-based filtering uses the same date format written by ingestion; consistent within the system |

## Migration Plan

1. Deploy CDK stack: 5 new Lambda functions, API Gateway routes, IAM read policies
2. No data migration required — reads existing data written by ingestion pipeline
3. Rollback: remove API Gateway routes; Lambda functions are stateless and can be deleted without side effects

## Future Implementations

### Scheduled LLM Disease Detection
A process running daily (e.g., EventBridge cron + Lambda) will analyze a user's last 90 days of health records using un LLM to identify potential diseases, anomalies, or correlations. 

**Architectural Approach:**
- **No DynamoDB Refactor:** By restricting analysis to a sliding 90-day window, this process naturally aligns with the current DynamoDB `Scatter-gather` limits, avoiding the need to scan up to 3 years of historical records or modify the `healthRecordsTable` schema.
- **No Vector DB Required:** Apple Watch metrics are highly structured time-series data. Instead of using embeddings or a Vector DB (which excel at semantic search), the data will be queried as raw JSON arrays and injected directly into the LLM's context window. Modern LLMs (with 128k+ token limits) can easily ingest 90 days of daily aggregates and raw events without issue.
