"""Unit tests for dashboard shared modules: query_utils, pagination, validation, aggregation."""
import unittest
from decimal import Decimal

from shared.pagination import (
    decode_cursor,
    decode_simple_cursor,
    encode_cursor,
    encode_simple_cursor,
)
from shared.validation import (
    ALLOWED_METRIC_TYPES,
    validate_date_range,
    validate_granularity,
    validate_limit,
    validate_metric_type,
)
from shared.aggregation import aggregate_daily, aggregate_summary


class TestPagination(unittest.TestCase):
    """Tests for cursor encoding/decoding."""

    def test_encode_cursor_returns_none_when_empty(self):
        self.assertIsNone(encode_cursor({}))

    def test_encode_decode_roundtrip(self):
        keys = {
            "0": {"PK": {"S": "USER#abc#SHARD#0"}, "SK": {"S": "RECORD#HR#2024-01-01"}},
            "3": {"PK": {"S": "USER#abc#SHARD#3"}, "SK": {"S": "RECORD#HR#2024-01-02"}},
        }
        encoded = encode_cursor(keys)
        self.assertIsNotNone(encoded)
        decoded = decode_cursor(encoded)
        self.assertEqual(decoded["0"]["PK"]["S"], "USER#abc#SHARD#0")
        self.assertEqual(decoded["3"]["SK"]["S"], "RECORD#HR#2024-01-02")

    def test_decode_cursor_empty_returns_empty(self):
        self.assertEqual(decode_cursor(None), {})
        self.assertEqual(decode_cursor(""), {})

    def test_decode_cursor_invalid_raises(self):
        with self.assertRaises(ValueError):
            decode_cursor("not-valid-base64!!!")

    def test_encode_simple_cursor_none(self):
        self.assertIsNone(encode_simple_cursor(None))

    def test_simple_cursor_roundtrip(self):
        key = {"PK": "USER#abc", "SK": "RECORD#ECG#2024-01-01"}
        encoded = encode_simple_cursor(key)
        decoded = decode_simple_cursor(encoded)
        self.assertEqual(decoded["PK"], "USER#abc")

    def test_decode_simple_cursor_none(self):
        self.assertIsNone(decode_simple_cursor(None))
        self.assertIsNone(decode_simple_cursor(""))

    def test_decode_simple_cursor_invalid_raises(self):
        with self.assertRaises(ValueError):
            decode_simple_cursor("bad-cursor!!!")


class TestValidation(unittest.TestCase):
    """Tests for input validation."""

    def test_validate_date_range_valid(self):
        start, end = validate_date_range("2024-01-01", "2024-03-01")
        self.assertEqual(start, "2024-01-01")
        self.assertEqual(end, "2024-03-01")

    def test_validate_date_range_same_day(self):
        start, end = validate_date_range("2024-01-01", "2024-01-01")
        self.assertEqual(start, "2024-01-01")

    def test_validate_date_range_exceeds_90_days(self):
        with self.assertRaises(ValueError) as ctx:
            validate_date_range("2024-01-01", "2024-06-01")
        self.assertIn("exceeds", str(ctx.exception).lower())

    def test_validate_date_range_invalid_format(self):
        with self.assertRaises(ValueError):
            validate_date_range("not-a-date", "2024-01-01")

    def test_validate_date_range_start_after_end(self):
        with self.assertRaises(ValueError):
            validate_date_range("2024-03-01", "2024-01-01")

    def test_validate_metric_type_valid(self):
        self.assertEqual(validate_metric_type("HeartRate"), "HeartRate")

    def test_validate_metric_type_invalid(self):
        with self.assertRaises(ValueError):
            validate_metric_type("NotAValidType")

    def test_validate_limit_default(self):
        self.assertEqual(validate_limit(None, 100, 1000), 100)

    def test_validate_limit_custom(self):
        self.assertEqual(validate_limit("500", 100, 1000), 500)

    def test_validate_limit_capped_at_max(self):
        self.assertEqual(validate_limit("5000", 100, 1000), 1000)

    def test_validate_limit_invalid(self):
        with self.assertRaises(ValueError):
            validate_limit("not-a-number", 100, 1000)

    def test_validate_limit_zero(self):
        with self.assertRaises(ValueError):
            validate_limit("0", 100, 1000)

    def test_validate_granularity_default(self):
        self.assertEqual(validate_granularity(None), "daily")

    def test_validate_granularity_daily(self):
        self.assertEqual(validate_granularity("daily"), "daily")

    def test_validate_granularity_raw(self):
        self.assertEqual(validate_granularity("raw"), "raw")

    def test_validate_granularity_invalid(self):
        with self.assertRaises(ValueError):
            validate_granularity("hourly")


class TestAggregation(unittest.TestCase):
    """Tests for aggregation utilities."""

    def test_aggregate_daily_basic(self):
        records = [
            {"startDate": "2024-01-01T08:00:00", "value": Decimal("70")},
            {"startDate": "2024-01-01T12:00:00", "value": Decimal("80")},
            {"startDate": "2024-01-02T08:00:00", "value": Decimal("65")},
        ]
        result = aggregate_daily(records)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["date"], "2024-01-01")
        self.assertEqual(result[0]["avg"], 75.0)
        self.assertEqual(result[0]["min"], 70.0)
        self.assertEqual(result[0]["max"], 80.0)
        self.assertEqual(result[0]["count"], 2)
        self.assertEqual(result[1]["date"], "2024-01-02")
        self.assertEqual(result[1]["avg"], 65.0)

    def test_aggregate_daily_empty(self):
        result = aggregate_daily([])
        self.assertEqual(result, [])

    def test_aggregate_daily_skips_none_values(self):
        records = [
            {"startDate": "2024-01-01T08:00:00", "value": None},
            {"startDate": "2024-01-01T12:00:00", "value": Decimal("80")},
        ]
        result = aggregate_daily(records)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["count"], 1)

    def test_aggregate_daily_sorted_output(self):
        records = [
            {"startDate": "2024-01-03T08:00:00", "value": Decimal("70")},
            {"startDate": "2024-01-01T08:00:00", "value": Decimal("60")},
            {"startDate": "2024-01-02T08:00:00", "value": Decimal("65")},
        ]
        result = aggregate_daily(records)
        dates = [r["date"] for r in result]
        self.assertEqual(dates, ["2024-01-01", "2024-01-02", "2024-01-03"])

    def test_aggregate_summary_basic(self):
        records = [
            {"value": Decimal("70")},
            {"value": Decimal("80")},
            {"value": Decimal("90")},
        ]
        result = aggregate_summary(records)
        self.assertIsNotNone(result)
        self.assertEqual(result["avg"], 80.0)
        self.assertEqual(result["min"], 70.0)
        self.assertEqual(result["max"], 90.0)
        self.assertEqual(result["count"], 3)

    def test_aggregate_summary_empty(self):
        result = aggregate_summary([])
        self.assertIsNone(result)

    def test_aggregate_summary_no_valid_values(self):
        records = [{"value": None}, {"value": None}]
        result = aggregate_summary(records)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
