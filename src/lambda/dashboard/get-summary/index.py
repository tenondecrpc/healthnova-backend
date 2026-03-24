"""GET /dashboard/summary — Composite health summary for last 7 days."""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3
from boto3.dynamodb.conditions import Key

from common import (
    create_error_response,
    create_success_response,
    get_logger,
    with_cors,
)
from shared.aggregation import aggregate_summary
from shared.query_utils import scatter_gather, query_jobs

logger = get_logger(__name__)

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("HEALTH_RECORDS_TABLE_NAME", "")
table = dynamodb.Table(table_name)

SUMMARY_METRIC_TYPES = ["HeartRate", "HeartRateVariabilitySDNN", "BloodPressureSystolic"]


def _get_user_id(event: Dict[str, Any]) -> str | None:
    """Extract user_id from the authorizer context."""
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    return authorizer.get("sub") or authorizer.get("principalId")


def _count_records(user_id: str, sk_prefix: str, start: str, end: str) -> int:
    """Count non-sharded records in a date range using Select='COUNT'."""
    pk = f"USER#{user_id}"
    sk_start = f"{sk_prefix}{start}"
    sk_end = f"{sk_prefix}{end}~"

    response = table.query(
        KeyConditionExpression=Key("PK").eq(pk) & Key("SK").between(sk_start, sk_end),
        Select="COUNT",
    )
    return response.get("Count", 0)


@with_cors()
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /dashboard/summary."""
    start_time = time.time()

    try:
        user_id = _get_user_id(event)
        if not user_id:
            return create_error_response(
                error_message="Unable to identify user",
                status_code=401,
                error_code="UNAUTHORIZED",
            )

        # Compute last-7-days period
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=7)
        start_date = start_dt.strftime("%Y-%m-%d")
        end_date = end_dt.strftime("%Y-%m-%d")

        results: Dict[str, Any] = {}
        errors: List[str] = []

        def _fetch_metric(metric_type: str) -> tuple:
            """Scatter-gather for a metric type."""
            try:
                result = scatter_gather(
                    user_id=user_id,
                    record_type=metric_type,
                    start_date=start_date,
                    end_date=end_date,
                )
                return (metric_type, aggregate_summary(result["items"]))
            except Exception as e:
                logger.error("Summary fetch failed for %s: %s", metric_type, str(e))
                return (metric_type, None)

        def _fetch_ecg_count() -> tuple:
            """Count ECG records."""
            try:
                count = _count_records(user_id, "RECORD#ECG#", start_date, end_date)
                return ("ecgCount", count)
            except Exception as e:
                logger.error("Summary ECG count failed: %s", str(e))
                return ("ecgCount", 0)

        def _fetch_workout_count() -> tuple:
            """Count GPX workout records."""
            try:
                count = _count_records(user_id, "RECORD#GPX#", start_date, end_date)
                return ("workoutCount", count)
            except Exception as e:
                logger.error("Summary workout count failed: %s", str(e))
                return ("workoutCount", 0)

        def _fetch_recent_jobs() -> tuple:
            """Get recent jobs."""
            try:
                jobs = query_jobs(user_id=user_id, limit=5)
                return ("recentJobs", jobs)
            except Exception as e:
                logger.error("Summary jobs fetch failed: %s", str(e))
                return ("recentJobs", [])

        # Execute all queries in parallel (up to 32 queries)
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = []

            # 3 metric types × 10 shards each (handled inside scatter_gather)
            for metric_type in SUMMARY_METRIC_TYPES:
                futures.append(executor.submit(_fetch_metric, metric_type))

            # ECG count (1 query)
            futures.append(executor.submit(_fetch_ecg_count))

            # GPX count (1 query)
            futures.append(executor.submit(_fetch_workout_count))

            # Recent jobs (1 query)
            futures.append(executor.submit(_fetch_recent_jobs))

            for future in as_completed(futures):
                key, value = future.result()
                results[key] = value

        # Build response
        summary = {
            "period": {"start": start_date, "end": end_date},
            "metrics": {
                "heartRate": results.get("HeartRate"),
                "hrv": results.get("HeartRateVariabilitySDNN"),
                "bloodPressure": results.get("BloodPressureSystolic"),
            },
            "ecgCount": results.get("ecgCount", 0),
            "workoutCount": results.get("workoutCount", 0),
            "recentJobs": results.get("recentJobs", []),
        }

        elapsed = round((time.time() - start_time) * 1000, 1)
        logger.info(
            "summary_query: period=%s..%s, elapsed_ms=%s",
            start_date, end_date, elapsed,
        )

        return create_success_response(
            data=summary,
            message="Dashboard summary retrieved successfully",
        )

    except Exception as e:
        logger.error("Error in get-summary: %s", str(e))
        return create_error_response(
            error_message="Failed to retrieve dashboard summary",
            status_code=500,
            error_code="INTERNAL_ERROR",
        )
