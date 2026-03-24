"""Input validation for dashboard query parameters."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

MAX_DATE_RANGE_DAYS = 90

ALLOWED_METRIC_TYPES = [
    "HeartRate",
    "HeartRateVariabilitySDNN",
    "BloodPressureSystolic",
    "BloodPressureDiastolic",
    "RestingHeartRate",
    "OxygenSaturation",
    "BodyTemperature",
    "RespiratoryRate",
    "StepCount",
    "DistanceWalkingRunning",
    "BasalEnergyBurned",
    "ActiveEnergyBurned",
    "FlightsClimbed",
    "BodyMass",
    "Height",
    "WalkingHeartRateAverage",
    "EnvironmentalAudioExposure",
    "HeadphoneAudioExposure",
    "WalkingSpeed",
    "WalkingStepLength",
    "WalkingDoubleSupportPercentage",
    "WalkingAsymmetryPercentage",
    "SixMinuteWalkTestDistance",
    "AppleStandTime",
    "AppleExerciseTime",
]

RAW_LIMIT_MAX = 1000
RAW_LIMIT_DEFAULT = 100

ECG_LIMIT_MAX = 200
ECG_LIMIT_DEFAULT = 50

WORKOUTS_LIMIT_MAX = 200
WORKOUTS_LIMIT_DEFAULT = 50


def parse_date(value: str) -> datetime:
    """Parse an ISO date string (YYYY-MM-DD).

    Raises:
        ValueError: If the string is not a valid date.
    """
    return datetime.strptime(value, "%Y-%m-%d")


def validate_date_range(start: str, end: str) -> Tuple[str, str]:
    """Validate and return start/end dates.

    Raises:
        ValueError: If dates are invalid or range exceeds MAX_DATE_RANGE_DAYS.
    """
    try:
        start_dt = parse_date(start)
    except ValueError:
        raise ValueError(f"Invalid start date format: {start}. Expected YYYY-MM-DD")

    try:
        end_dt = parse_date(end)
    except ValueError:
        raise ValueError(f"Invalid end date format: {end}. Expected YYYY-MM-DD")

    if start_dt > end_dt:
        raise ValueError("start date must be before or equal to end date")

    delta = (end_dt - start_dt).days
    if delta > MAX_DATE_RANGE_DAYS:
        raise ValueError(
            f"Date range exceeds maximum of {MAX_DATE_RANGE_DAYS} days (requested {delta} days)"
        )

    return start, end


def validate_metric_type(metric_type: str) -> str:
    """Validate that the metric type is in the allowed whitelist.

    Raises:
        ValueError: If metric_type is not allowed.
    """
    if metric_type not in ALLOWED_METRIC_TYPES:
        raise ValueError(
            f"Invalid metric type: {metric_type}. "
            f"Allowed types: {', '.join(ALLOWED_METRIC_TYPES)}"
        )
    return metric_type


def validate_limit(value: Optional[str], default: int, maximum: int) -> int:
    """Parse and validate limit query parameter.

    Args:
        value: Raw query parameter value (string or None).
        default: Default limit if value is None.
        maximum: Maximum allowed limit.

    Returns:
        Validated limit integer.

    Raises:
        ValueError: If value is not a valid positive integer.
    """
    if value is None:
        return default

    try:
        limit = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid limit value: {value}. Must be a positive integer")

    if limit < 1:
        raise ValueError("limit must be at least 1")

    return min(limit, maximum)


def validate_granularity(value: Optional[str]) -> str:
    """Validate granularity parameter.

    Returns:
        'daily' or 'raw'.

    Raises:
        ValueError: If value is not 'daily' or 'raw'.
    """
    if value is None:
        return "daily"

    if value not in ("daily", "raw"):
        raise ValueError(f"Invalid granularity: {value}. Must be 'daily' or 'raw'")

    return value
