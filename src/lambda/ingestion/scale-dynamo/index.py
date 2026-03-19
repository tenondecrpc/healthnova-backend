import os
import time
from typing import Any, Dict

import boto3

from common import get_logger

logger = get_logger(__name__)

dynamodb = boto3.client("dynamodb")
TABLE_NAME = os.environ["HEALTH_RECORDS_TABLE_NAME"]
WCU_HIGH = int(os.environ.get("WCU_HIGH", "10000"))
WCU_LOW = int(os.environ.get("WCU_LOW", "5"))
RCU = int(os.environ.get("RCU", "100"))
GSI_NAME = os.environ.get("GSI_NAME", "UserTypeIndex")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    action = event.get("action", "up")
    wcu = WCU_HIGH if action == "up" else WCU_LOW

    current_wcu = dynamodb.describe_table(TableName=TABLE_NAME)["Table"]["ProvisionedThroughput"]["WriteCapacityUnits"]
    logger.info("Scaling table %s: current WCU=%d, target WCU=%d (action=%s)", TABLE_NAME, current_wcu, wcu, action)

    if action == "up" and current_wcu >= wcu:
        logger.info("Table already at WCU=%d >= target %d, skipping scale-up", current_wcu, wcu)
        return {"scaled": False, "skipped": True, "wcu": current_wcu}

    try:
        dynamodb.update_table(
            TableName=TABLE_NAME,
            ProvisionedThroughput={"ReadCapacityUnits": RCU, "WriteCapacityUnits": wcu},
            GlobalSecondaryIndexUpdates=[{
                "Update": {
                    "IndexName": GSI_NAME,
                    "ProvisionedThroughput": {"ReadCapacityUnits": RCU, "WriteCapacityUnits": wcu},
                }
            }],
        )
    except Exception as e:
        if action != "down":
            raise
        logger.warning("ScaleDynamoDown failed, skipping: %s", e)
        return {"scaled": False, "skipped": True, "wcu": wcu}

    _wait_active()
    logger.info("Table %s ready at WCU=%d", TABLE_NAME, wcu)

    return {"scaled": True, "wcu": wcu}


def _wait_active() -> None:
    for _ in range(60):
        status = dynamodb.describe_table(TableName=TABLE_NAME)["Table"]["TableStatus"]
        if status == "ACTIVE":
            return
        time.sleep(5)
    raise TimeoutError(f"Table {TABLE_NAME} did not become ACTIVE within 5 minutes")
