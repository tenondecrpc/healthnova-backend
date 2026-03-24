"""Scatter-gather helper for querying sharded DynamoDB health records."""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Key

from common import get_logger

logger = get_logger(__name__)

NUM_SHARDS = 10

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("HEALTH_RECORDS_TABLE_NAME", "")
table = dynamodb.Table(table_name)


def scatter_gather(
    user_id: str,
    record_type: str,
    start_date: str,
    end_date: str,
    limit_per_shard: Optional[int] = None,
    cursors: Optional[Dict[str, dict]] = None,
) -> Dict[str, Any]:
    """Execute parallel DynamoDB queries across all 10 shards.

    Args:
        user_id: Authenticated user ID.
        record_type: Health record type (e.g. HeartRate).
        start_date: ISO date string for range start.
        end_date: ISO date string for range end.
        limit_per_shard: Optional per-shard limit for raw pagination.
        cursors: Dict mapping shard index (str) to LastEvaluatedKey for resumption.

    Returns:
        Dict with ``items`` (merged sorted list) and ``last_keys`` (per-shard
        LastEvaluatedKey for cursor encoding; exhausted shards omitted).
    """
    if cursors is None:
        cursors = {}

    sk_start = f"RECORD#{record_type}#{start_date}"
    sk_end = f"RECORD#{record_type}#{end_date}~"  # ~ is after all ISO timestamps

    def _query_shard(shard_index: int) -> Dict[str, Any]:
        shard_str = str(shard_index)

        # If we have cursors and this shard is not in them, it's exhausted
        if cursors and shard_str not in cursors:
            return {"items": [], "last_key": None, "shard": shard_str}

        pk = f"USER#{user_id}#SHARD#{shard_index}"
        kwargs: Dict[str, Any] = {
            "KeyConditionExpression": Key("PK").eq(pk) & Key("SK").between(sk_start, sk_end),
        }

        if limit_per_shard:
            kwargs["Limit"] = limit_per_shard

        if shard_str in cursors:
            kwargs["ExclusiveStartKey"] = cursors[shard_str]

        response = table.query(**kwargs)
        return {
            "items": response.get("Items", []),
            "last_key": response.get("LastEvaluatedKey"),
            "shard": shard_str,
        }

    all_items: List[Dict[str, Any]] = []
    last_keys: Dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=NUM_SHARDS) as executor:
        futures = {executor.submit(_query_shard, i): i for i in range(NUM_SHARDS)}
        for future in as_completed(futures):
            result = future.result()
            all_items.extend(result["items"])
            if result["last_key"]:
                last_keys[result["shard"]] = result["last_key"]

    # Sort merged results by startDate (stored in SK or as an attribute)
    all_items.sort(key=lambda x: x.get("startDate", x.get("SK", "")))

    logger.info(
        "scatter_gather complete: type=%s, shards=10, total_records=%d, exhausted_shards=%d",
        record_type,
        len(all_items),
        NUM_SHARDS - len(last_keys) if cursors else 0,
    )

    return {"items": all_items, "last_keys": last_keys}


def query_non_sharded(
    user_id: str,
    sk_prefix: str,
    start_date: str,
    end_date: str,
    limit: int = 50,
    cursor: Optional[dict] = None,
) -> Dict[str, Any]:
    """Query non-sharded records (ECG, GPX, JOB) on PK=USER#{userId}.

    Args:
        user_id: Authenticated user ID.
        sk_prefix: SK prefix (e.g. RECORD#ECG#, RECORD#GPX#, JOB#).
        start_date: ISO date string for range start.
        end_date: ISO date string for range end.
        limit: Max items to return.
        cursor: DynamoDB LastEvaluatedKey for resumption.

    Returns:
        Dict with ``items`` and ``last_key``.
    """
    pk = f"USER#{user_id}"
    sk_start = f"{sk_prefix}{start_date}"
    sk_end = f"{sk_prefix}{end_date}~"

    kwargs: Dict[str, Any] = {
        "KeyConditionExpression": Key("PK").eq(pk) & Key("SK").between(sk_start, sk_end),
        "Limit": limit,
    }

    if cursor:
        kwargs["ExclusiveStartKey"] = cursor

    response = table.query(**kwargs)

    return {
        "items": response.get("Items", []),
        "last_key": response.get("LastEvaluatedKey"),
    }


def query_jobs(
    user_id: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Query job records sorted by updatedAt descending.

    Args:
        user_id: Authenticated user ID.
        limit: Max jobs to return.

    Returns:
        List of job items sorted by updatedAt desc.
    """
    pk = f"USER#{user_id}"

    response = table.query(
        KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("JOB#"),
        Limit=limit,
        ScanIndexForward=False,
    )

    items = response.get("Items", [])
    # Sort by updatedAt descending
    items.sort(key=lambda x: x.get("updatedAt", ""), reverse=True)

    return items
