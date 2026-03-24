"""Daily aggregation utilities for health metric records."""
from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional


def aggregate_daily(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group records by date and compute avg/min/max/count per day.

    Expects each record to have a ``startDate`` (ISO datetime string) and
    a numeric ``value`` field.

    Args:
        records: List of raw health metric records.

    Returns:
        Sorted list of daily aggregates with keys:
        ``date``, ``avg``, ``min``, ``max``, ``count``.
    """
    daily: Dict[str, List[float]] = defaultdict(list)

    for record in records:
        start_date = record.get("startDate", "")
        # Extract date portion (YYYY-MM-DD) from ISO datetime
        date_key = start_date[:10] if start_date else "unknown"

        value = record.get("value")
        if value is not None:
            try:
                numeric_value = float(Decimal(str(value)))
                daily[date_key].append(numeric_value)
            except (ValueError, TypeError, ArithmeticError):
                continue

    aggregated: List[Dict[str, Any]] = []
    for date_key in sorted(daily.keys()):
        values = daily[date_key]
        if not values:
            continue

        aggregated.append({
            "date": date_key,
            "avg": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "count": len(values),
        })

    return aggregated


def aggregate_summary(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Compute aggregate statistics across all records for a summary.

    Args:
        records: List of raw health metric records with ``value`` field.

    Returns:
        Dict with ``avg``, ``min``, ``max``, ``count``, or None if no valid values.
    """
    values: List[float] = []
    for record in records:
        value = record.get("value")
        if value is not None:
            try:
                values.append(float(Decimal(str(value))))
            except (ValueError, TypeError, ArithmeticError):
                continue

    if not values:
        return None

    return {
        "avg": round(sum(values) / len(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "count": len(values),
    }
