"""Unit tests for GET /dashboard/ecg Lambda."""
import json
import sys
import unittest
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
    mod_name = "get-ecg.index"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return import_module(mod_name).handler


class TestGetEcg(unittest.TestCase):

    @patch("shared.query_utils.query_non_sharded")
    def test_pagination(self, mock_query):
        mock_query.return_value = {
            "items": [{"PK": "USER#abc", "SK": "RECORD#ECG#2024-01-01", "classification": "SinusRhythm"}],
            "last_key": {"PK": "USER#abc", "SK": "RECORD#ECG#2024-01-01"},
        }
        handler = _get_handler()
        response = handler(_make_event({"start": "2024-01-01", "end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body["data"]), 1)

    def test_missing_start(self):
        handler = _get_handler()
        response = handler(_make_event({"end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 400)

    def test_missing_end(self):
        handler = _get_handler()
        response = handler(_make_event({"start": "2024-01-01"}), None)
        self.assertEqual(response["statusCode"], 400)

    def test_date_range_exceeded(self):
        handler = _get_handler()
        response = handler(_make_event({"start": "2024-01-01", "end": "2024-06-01"}), None)
        self.assertEqual(response["statusCode"], 400)

    @patch("shared.query_utils.query_non_sharded")
    def test_empty_results(self, mock_query):
        mock_query.return_value = {"items": [], "last_key": None}
        handler = _get_handler()
        response = handler(_make_event({"start": "2024-01-01", "end": "2024-01-31"}), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["data"], [])

    def test_unauthenticated(self):
        handler = _get_handler()
        event = _make_event({"start": "2024-01-01", "end": "2024-01-31"})
        event["requestContext"]["authorizer"] = {}
        response = handler(event, None)
        self.assertEqual(response["statusCode"], 401)


if __name__ == "__main__":
    unittest.main()
