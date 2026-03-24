"""Cursor encoding/decoding for multi-shard pagination."""
import base64
import json
from typing import Any, Dict, Optional

from common import get_logger

logger = get_logger(__name__)


def encode_cursor(last_keys: Dict[str, dict]) -> Optional[str]:
    """Encode per-shard LastEvaluatedKey objects into a single base64 cursor.

    Exhausted shards (no LastEvaluatedKey) are omitted.

    Args:
        last_keys: Mapping of shard index (str) to DynamoDB LastEvaluatedKey.

    Returns:
        Base64-encoded JSON string, or None if all shards are exhausted.
    """
    if not last_keys:
        return None

    payload = json.dumps(last_keys, default=str)
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: Optional[str]) -> Dict[str, dict]:
    """Decode a base64 cursor back into per-shard LastEvaluatedKey objects.

    Args:
        cursor: Base64-encoded cursor string from a previous response.

    Returns:
        Dict mapping shard index (str) to LastEvaluatedKey.

    Raises:
        ValueError: If the cursor is malformed.
    """
    if not cursor:
        return {}

    try:
        payload = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        decoded = json.loads(payload)
        if not isinstance(decoded, dict):
            raise ValueError("Cursor payload is not a dict")
        return decoded
    except (json.JSONDecodeError, UnicodeDecodeError, Exception) as exc:
        logger.warning("Failed to decode cursor: %s", str(exc))
        raise ValueError(f"Invalid cursor: {str(exc)}") from exc


def encode_simple_cursor(last_key: Optional[dict]) -> Optional[str]:
    """Encode a single DynamoDB LastEvaluatedKey into a base64 cursor.

    Used for non-sharded queries (ECG, GPX).

    Args:
        last_key: DynamoDB LastEvaluatedKey dict.

    Returns:
        Base64-encoded JSON string, or None if no more pages.
    """
    if not last_key:
        return None

    payload = json.dumps(last_key, default=str)
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")


def decode_simple_cursor(cursor: Optional[str]) -> Optional[dict]:
    """Decode a single-key cursor back into a DynamoDB LastEvaluatedKey.

    Args:
        cursor: Base64-encoded cursor string.

    Returns:
        LastEvaluatedKey dict, or None if cursor is empty.

    Raises:
        ValueError: If the cursor is malformed.
    """
    if not cursor:
        return None

    try:
        payload = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        decoded = json.loads(payload)
        if not isinstance(decoded, dict):
            raise ValueError("Cursor payload is not a dict")
        return decoded
    except (json.JSONDecodeError, UnicodeDecodeError, Exception) as exc:
        logger.warning("Failed to decode simple cursor: %s", str(exc))
        raise ValueError(f"Invalid cursor: {str(exc)}") from exc
