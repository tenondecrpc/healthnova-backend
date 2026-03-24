"""Unit tests for GET /dashboard/jobs Lambda."""
import json
import sys
import unittest
from importlib import import_module
from unittest.mock import patch


def _make_event(user_id="test-user-123"):
    return {
        "httpMethod": "GET",
        "queryStringParameters": None,
        "requestContext": {"authorizer": {"sub": user_id}},
        "headers": {},
    }


def _get_handler():
    mod_name = "get-jobs.index"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return import_module(mod_name).handler


class TestGetJobs(unittest.TestCase):

    @patch("shared.query_utils.query_jobs")
    def test_jobs_returned_sorted(self, mock_query_jobs):
        mock_query_jobs.return_value = [
            {"PK": "USER#abc", "SK": "JOB#j2", "status": "COMPLETED", "updatedAt": "1704067300"},
            {"PK": "USER#abc", "SK": "JOB#j1", "status": "FAILED", "updatedAt": "1704067200"},
        ]
        handler = _get_handler()
        response = handler(_make_event(), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body["data"]), 2)

    @patch("shared.query_utils.query_jobs")
    def test_empty_results(self, mock_query_jobs):
        mock_query_jobs.return_value = []
        handler = _get_handler()
        response = handler(_make_event(), None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["data"], [])

    def test_unauthenticated(self):
        handler = _get_handler()
        event = _make_event()
        event["requestContext"]["authorizer"] = {}
        response = handler(event, None)
        self.assertEqual(response["statusCode"], 401)


if __name__ == "__main__":
    unittest.main()
