import os
import time
from typing import Any, Dict

import boto3

from common import get_logger

logger = get_logger(__name__)
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("HEALTH_RECORDS_TABLE_NAME", "")
table = dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Write final job status (COMPLETED or FAILED) to DynamoDB."""
    user_id = event["userId"]
    job_id = event["jobId"]
    status = event.get("status", "COMPLETED")
    error_step = event.get("errorStep")

    logger.info(
        "Marking job %s as %s for user %s", job_id, status, user_id
    )

    item = {
        "PK": f"USER#{user_id}",
        "SK": f"JOB#{job_id}",
        "GSI1SK": f"JOB#{job_id}",
        "status": status,
        "updatedAt": str(int(time.time())),
    }

    if error_step:
        item["errorStep"] = error_step

    table.put_item(Item=item)

    logger.info("Job %s marked as %s", job_id, status)

    return {
        "userId": user_id,
        "jobId": job_id,
        "status": status,
    }
