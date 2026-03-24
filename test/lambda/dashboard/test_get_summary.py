"""Unit tests for GET /dashboard/summary Lambda."""
import json
import sys
import unittest
from decimal import Decimal
from importlib import import_module
from unittest.mock import MagicMock, patch


def _make_event(user_id="test-user-123"):
    return {
        "httpMethod": "GET",
        "queryStringParameters": None,
        "requestContext": {"authorizer": {"sub": user_id}},
        "headers": {},
    }


def _get_handler():
    mod_name = "get-summary.index"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return import_module(mod_name).handler


class TestGetSummary(unittest.TestCase):

    @patch("shared.query_utils.query_jobs")
    @patch("shared.query_utils.scatter_gather")
    def test_full_summary(self, mock_scatter, mock_jobs):
        mock_scatter.return_value = {
            "items": [
                {"value": Decimal("70"), "startDate": "2024-01-01T08:00:00"},
                {"value": Decimal("80"), "startDate": "2024-01-01T12:00:00"},
            ],
            "last_keys": {},
        }
        mock_jobs.return_value = [
            {"SK": "JOB#j1", "status": "COMPLETED", "updatedAt": "1704067200"},
        ]

        handler = _get_handler()
        # Mock the table.query for ECG/GPX counts
        mod = sys.modules["get-summary.index"]
        mod.table = MagicMock()
        mod.table.query.return_value = {"Count": 5}

        response = handler(_make_event(), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertTrue(body["success"])

    @patch("shared.query_utils.query_jobs")
    @patch("shared.query_utils.scatter_gather")
    def test_empty_data(self, mock_scatter, mock_jobs):
        mock_scatter.return_value = {"items": [], "last_keys": {}}
        mock_jobs.return_value = []

        handler = _get_handler()
        mod = sys.modules["get-summary.index"]
        mod.table = MagicMock()
        mod.table.query.return_value = {"Count": 0}

        response = handler(_make_event(), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["data"]["ecgCount"], 0)
        self.assertEqual(body["data"]["workoutCount"], 0)

    @patch("shared.query_utils.query_jobs")
    @patch("shared.query_utils.scatter_gather")
    def test_partial_failures(self, mock_scatter, mock_jobs):
        call_count = [0]
        def side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Shard timeout")
            return {"items": [{"value": Decimal("75"), "startDate": "2024-01-01"}], "last_keys": {}}

        mock_scatter.side_effect = side_effect
        mock_jobs.return_value = []

        handler = _get_handler()
        mod = sys.modules["get-summary.index"]
        mod.table = MagicMock()
        mod.table.query.return_value = {"Count": 0}

        response = handler(_make_event(), None)
        self.assertEqual(response["statusCode"], 200)

    def test_unauthenticated(self):
        handler = _get_handler()
        event = _make_event()
        event["requestContext"]["authorizer"] = {}
        response = handler(event, None)
        self.assertEqual(response["statusCode"], 401)


if __name__ == "__main__":
    unittest.main()
