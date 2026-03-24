"""GET /dashboard/ecg — Query ECG records with pagination."""
import os
import sys
import time
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common import (
    create_error_response,
    create_success_response,
    get_logger,
    with_cors,
)
from shared.pagination import decode_simple_cursor, encode_simple_cursor
from shared.query_utils import query_non_sharded
from shared.validation import (
    ECG_LIMIT_DEFAULT,
    ECG_LIMIT_MAX,
    validate_date_range,
    validate_limit,
)

logger = get_logger(__name__)


def _get_user_id(event: Dict[str, Any]) -> str | None:
    """Extract user_id from the authorizer context."""
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    return authorizer.get("sub") or authorizer.get("principalId")


@with_cors()
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /dashboard/ecg."""
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
            limit = validate_limit(params.get("limit"), ECG_LIMIT_DEFAULT, ECG_LIMIT_MAX)
        except ValueError as e:
            return create_error_response(
                error_message=str(e),
                status_code=400,
                error_code="INVALID_LIMIT",
            )

        try:
            cursor = decode_simple_cursor(params.get("cursor"))
        except ValueError:
            return create_error_response(
                error_message="Invalid cursor",
                status_code=400,
                error_code="INVALID_CURSOR",
            )

        # Query ECG records (non-sharded)
        result = query_non_sharded(
            user_id=user_id,
            sk_prefix="RECORD#ECG#",
            start_date=start,
            end_date=end,
            limit=limit,
            cursor=cursor,
        )

        items = result["items"]
        next_cursor = encode_simple_cursor(result["last_key"])

        elapsed = round((time.time() - start_time) * 1000, 1)
        logger.info(
            "ecg_query: range=%s..%s, records=%d, elapsed_ms=%s",
            start, end, len(items), elapsed,
        )

        return create_success_response(
            data=items,
            message="ECG records retrieved successfully",
            metadata={
                "period": {"start": start, "end": end},
                "count": len(items),
                "nextCursor": next_cursor,
            },
        )

    except Exception as e:
        logger.error("Error in get-ecg: %s", str(e))
        return create_error_response(
            error_message="Failed to retrieve ECG records",
            status_code=500,
            error_code="INTERNAL_ERROR",
        )
