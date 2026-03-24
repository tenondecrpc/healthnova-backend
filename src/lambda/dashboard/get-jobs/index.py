"""GET /dashboard/jobs — List ingestion job history."""
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
from shared.query_utils import query_jobs

logger = get_logger(__name__)


def _get_user_id(event: Dict[str, Any]) -> str | None:
    """Extract user_id from the authorizer context."""
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    return authorizer.get("sub") or authorizer.get("principalId")


@with_cors()
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /dashboard/jobs."""
    start_time = time.time()

    try:
        user_id = _get_user_id(event)
        if not user_id:
            return create_error_response(
                error_message="Unable to identify user",
                status_code=401,
                error_code="UNAUTHORIZED",
            )

        # Query jobs (sorted by updatedAt desc, limit 20)
        items = query_jobs(user_id=user_id, limit=20)

        elapsed = round((time.time() - start_time) * 1000, 1)
        logger.info(
            "jobs_query: records=%d, elapsed_ms=%s",
            len(items), elapsed,
        )

        return create_success_response(
            data=items,
            message="Jobs retrieved successfully",
            metadata={
                "count": len(items),
            },
        )

    except Exception as e:
        logger.error("Error in get-jobs: %s", str(e))
        return create_error_response(
            error_message="Failed to retrieve jobs",
            status_code=500,
            error_code="INTERNAL_ERROR",
        )
