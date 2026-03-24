"""Shared test fixtures for dashboard Lambda tests.

Sets up mock 'common' module before any Lambda handler is imported.
"""
import json
import os
import sys
from types import ModuleType
from unittest.mock import MagicMock

# Set environment
os.environ["HEALTH_RECORDS_TABLE_NAME"] = "test-health-records"

# Build a proper mock common module that behaves like the real one
_common = ModuleType("common")


def _mock_get_logger(name=None):
    return MagicMock()


def _mock_with_cors(*args, **kwargs):
    """Passthrough decorator that mimics @with_cors()."""
    def decorator(fn):
        return fn
    return decorator


def _mock_create_success_response(data=None, message="Success", status_code=200, headers=None, metadata=None):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    if metadata:
        body["metadata"] = metadata
    return {
        "statusCode": status_code,
        "body": json.dumps(body, default=str),
    }


def _mock_create_error_response(error_message, status_code=400, error_code=None, details=None, headers=None):
    body = {
        "success": False,
        "error": {
            "message": error_message,
            "code": error_code or f"ERROR_{status_code}",
        },
    }
    if details:
        body["error"]["details"] = details
    return {
        "statusCode": status_code,
        "body": json.dumps(body, default=str),
    }


# Assign functions to the mock module
_common.get_logger = _mock_get_logger
_common.setup_logger = _mock_get_logger
_common.log_request_metadata = MagicMock()
_common.log_error = MagicMock()
_common.with_cors = _mock_with_cors
_common.create_response = MagicMock()
_common.create_success_response = _mock_create_success_response
_common.create_error_response = _mock_create_error_response
_common.create_validation_error_response = MagicMock()
_common.create_not_found_response = MagicMock()
_common.create_unauthorized_response = MagicMock()
_common.create_forbidden_response = MagicMock()
_common.create_internal_error_response = MagicMock()
_common.create_paginated_response = MagicMock()

# Register in sys.modules before anything imports it
sys.modules["common"] = _common

# Add Lambda source to path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_project_root, "src", "lambda", "dashboard"))
