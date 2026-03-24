"""Unit tests for GET /dashboard/metrics Lambda."""
import json
import sys
import unittest
from decimal import Decimal
from importlib import import_module
from unittest.mock import patch


def _make_event(query_params=None, user_id="test-user-123"):
    return {
        "httpMethod": "GET",
        "queryStringParameters": query_params,
        "requestContext": {"authorizer": {"sub": user_id}},
        "headers": {},
    }


def _get_handler():
    # Force reimport to get a fresh module
    mod_name = "get-metrics.index"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return import_module(mod_name).handler


class TestGetMetrics(unittest.TestCase):

    @patch("shared.query_utils.scatter_gather")
    def test_daily_aggregation(self, mock_scatter):
        mock_scatter.return_value = {
            "items": [
                {"startDate": "2024-01-01T08:00:00", "value": Decimal("70"), "unit": "count/min"},
                {"startDate": "2024-01-01T12:00:00", "value": Decimal("80"), "unit": "count/min"},
                {"startDate": "2024-01-02T08:00:00", "value": Decimal("65"), "unit": "count/min"},
            ],
            "last_keys": {},
        }
        handler = _get_handler()
        response = handler(_make_event({"type": "HeartRate", "start": "2024-01-01", "end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertTrue(body["success"])
        self.assertEqual(len(body["data"]), 2)

    @patch("shared.query_utils.scatter_gather")
    def test_raw_pagination(self, mock_scatter):
        mock_scatter.return_value = {
            "items": [{"startDate": "2024-01-01T08:00:00", "value": Decimal("70")}],
            "last_keys": {"0": {"PK": "USER#abc#SHARD#0", "SK": "RECORD#HR#2024-01-01"}},
        }
        handler = _get_handler()
        response = handler(
            _make_event({"type": "HeartRate", "start": "2024-01-01", "end": "2024-01-31", "granularity": "raw"}), None
        )
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIsNotNone(body["metadata"]["nextCursor"])

    def test_missing_type_parameter(self):
        handler = _get_handler()
        response = handler(_make_event({"start": "2024-01-01", "end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 400)

    def test_missing_start_parameter(self):
        handler = _get_handler()
        response = handler(_make_event({"type": "HeartRate", "end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 400)

    def test_missing_end_parameter(self):
        handler = _get_handler()
        response = handler(_make_event({"type": "HeartRate", "start": "2024-01-01"}), None)
        self.assertEqual(response["statusCode"], 400)

    def test_invalid_metric_type(self):
        handler = _get_handler()
        response = handler(_make_event({"type": "InvalidType", "start": "2024-01-01", "end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertEqual(body["error"]["code"], "INVALID_METRIC_TYPE")

    def test_date_range_exceeded(self):
        handler = _get_handler()
        response = handler(_make_event({"type": "HeartRate", "start": "2024-01-01", "end": "2024-06-01"}), None)
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertEqual(body["error"]["code"], "DATE_RANGE_EXCEEDED")

    def test_unauthenticated(self):
        handler = _get_handler()
        event = _make_event({"type": "HeartRate", "start": "2024-01-01", "end": "2024-01-31"})
        event["requestContext"]["authorizer"] = {}
        response = handler(event, None)
        self.assertEqual(response["statusCode"], 401)

    @patch("shared.query_utils.scatter_gather")
    def test_empty_results(self, mock_scatter):
        mock_scatter.return_value = {"items": [], "last_keys": {}}
        handler = _get_handler()
        response = handler(_make_event({"type": "HeartRate", "start": "2024-01-01", "end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["data"], [])


if __name__ == "__main__":
    unittest.main()
