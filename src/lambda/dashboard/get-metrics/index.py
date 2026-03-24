"""GET /dashboard/metrics — Query health metrics by type with scatter-gather."""
import os
import sys
import time
from typing import Any, Dict

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common import (
    create_error_response,
    create_success_response,
    get_logger,
    with_cors,
)
from shared.aggregation import aggregate_daily
from shared.pagination import decode_cursor, encode_cursor
from shared.query_utils import scatter_gather
from shared.validation import (
    RAW_LIMIT_DEFAULT,
    RAW_LIMIT_MAX,
    validate_date_range,
    validate_granularity,
    validate_limit,
    validate_metric_type,
)

logger = get_logger(__name__)


def _get_user_id(event: Dict[str, Any]) -> str | None:
    """Extract user_id from the authorizer context."""
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    return authorizer.get("sub") or authorizer.get("principalId")


@with_cors()
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /dashboard/metrics."""
    start_time = time.time()

    try:
        user_id = _get_user_id(event)
        if not user_id:
            return create_error_response(
                error_message="Unable to identify user",
                status_code=401,
                error_code="UNAUTHORIZED",
            )

        params = event.get("queryStringParameters") or {}

        # Validate required parameters
        metric_type = params.get("type")
        if not metric_type:
            return create_error_response(
                error_message="Missing required parameter: type",
                status_code=400,
                error_code="MISSING_PARAMETER",
            )

        start = params.get("start")
        if not start:
            return create_error_response(
                error_message="Missing required parameter: start",
                status_code=400,
                error_code="MISSING_PARAMETER",
            )

        end = params.get("end")
        if not end:
            return create_error_response(
                error_message="Missing required parameter: end",
                status_code=400,
                error_code="MISSING_PARAMETER",
            )

        # Validate inputs
        try:
            validate_metric_type(metric_type)
        except ValueError:
            return create_error_response(
                error_message=f"Invalid metric type: {metric_type}",
                status_code=400,
                error_code="INVALID_METRIC_TYPE",
            )

        try:
            validate_date_range(start, end)
        except ValueError as e:
            error_code = "DATE_RANGE_EXCEEDED" if "exceeds" in str(e).lower() else "INVALID_DATE"
            return create_error_response(
                error_message=str(e),
                status_code=400,
                error_code=error_code,
            )

        try:
            granularity = validate_granularity(params.get("granularity"))
        except ValueError as e:
            return create_error_response(
                error_message=str(e),
                status_code=400,
                error_code="INVALID_GRANULARITY",
            )

        if granularity == "raw":
            # Raw paginated mode
            try:
                limit = validate_limit(params.get("limit"), RAW_LIMIT_DEFAULT, RAW_LIMIT_MAX)
            except ValueError as e:
                return create_error_response(
                    error_message=str(e),
                    status_code=400,
                    error_code="INVALID_LIMIT",
                )

            try:
                cursors = decode_cursor(params.get("cursor"))
            except ValueError:
                return create_error_response(
                    error_message="Invalid cursor",
                    status_code=400,
                    error_code="INVALID_CURSOR",
                )

            # Distribute limit across shards
            per_shard_limit = max(1, limit // 10 + 1)
            result = scatter_gather(
                user_id=user_id,
                record_type=metric_type,
                start_date=start,
                end_date=end,
                limit_per_shard=per_shard_limit,
                cursors=cursors if cursors else None,
            )

            items = result["items"][:limit]
            next_cursor = encode_cursor(result["last_keys"])

            elapsed = round((time.time() - start_time) * 1000, 1)
            logger.info(
                "metrics_raw: type=%s, range=%s..%s, records=%d, elapsed_ms=%s",
                metric_type, start, end, len(items), elapsed,
            )

            return create_success_response(
                data=items,
                message="Metrics retrieved successfully",
                metadata={
                    "type": metric_type,
                    "granularity": "raw",
                    "period": {"start": start, "end": end},
                    "count": len(items),
                    "nextCursor": next_cursor,
                },
            )
        else:
            # Daily aggregation mode (default)
            result = scatter_gather(
                user_id=user_id,
                record_type=metric_type,
                start_date=start,
                end_date=end,
            )

            aggregated = aggregate_daily(result["items"])

            elapsed = round((time.time() - start_time) * 1000, 1)
            logger.info(
                "metrics_daily: type=%s, range=%s..%s, raw_records=%d, daily_points=%d, elapsed_ms=%s",
                metric_type, start, end, len(result["items"]), len(aggregated), elapsed,
            )

            # Determine unit from first record if available
            unit = None
            if result["items"]:
                unit = result["items"][0].get("unit")

            return create_success_response(
                data=aggregated,
                message="Metrics retrieved successfully",
                metadata={
                    "type": metric_type,
                    "granularity": "daily",
                    "period": {"start": start, "end": end},
                    "count": len(aggregated),
                    "unit": unit,
                },
            )

    except Exception as e:
        logger.error("Error in get-metrics: %s", str(e))
        return create_error_response(
            error_message="Failed to retrieve metrics",
            status_code=500,
            error_code="INTERNAL_ERROR",
        )
