"""Tests for validation error handling."""

import json
import unittest
from unittest.mock import Mock

from openapi_client.exceptions import UnprocessableEntityException
from openapi_client.models.http_validation_error import HTTPValidationError
from openapi_client.models.validation_error import ValidationError
from openapi_client.models.validation_error_loc_inner import ValidationErrorLocInner

from dhl_sdk.exceptions import ValidationException
from dhl_sdk.error_handler import handle_validation_errors


class TestValidationErrors(unittest.TestCase):
    """Test suite for validation error handling."""

    def test_validation_exception_creation(self):
        """Test creating a ValidationException with HTTPValidationError."""
        # Create a mock validation error
        loc_inner = ValidationErrorLocInner(actual_instance="body")
        error = ValidationError(
            loc=[loc_inner],
            msg="Field required",
            type="value_error.missing",
        )
        http_error = HTTPValidationError(detail=[error])

        # Create exception
        exc = ValidationException(http_error, Exception("original"))

        # Verify attributes
        self.assertIsNotNone(exc.validation_error)
        self.assertEqual(len(exc.validation_error.detail), 1)
        self.assertIn("Field required", str(exc))

    def test_validation_exception_formatting(self):
        """Test that ValidationException formats errors nicely."""
        # Create validation errors
        loc_inner1 = ValidationErrorLocInner(actual_instance="body")
        loc_inner2 = ValidationErrorLocInner(actual_instance="name")
        error1 = ValidationError(
            loc=[loc_inner1, loc_inner2],
            msg="String too short",
            type="value_error.any_str.min_length",
        )

        loc_inner3 = ValidationErrorLocInner(actual_instance="query")
        loc_inner4 = ValidationErrorLocInner(actual_instance="limit")
        error2 = ValidationError(
            loc=[loc_inner3, loc_inner4],
            msg="Value must be greater than 0",
            type="value_error.number.not_gt",
        )

        http_error = HTTPValidationError(detail=[error1, error2])
        exc = ValidationException(http_error, Exception("original"))

        # Check formatting
        error_msg = str(exc)
        self.assertIn("API validation failed:", error_msg)
        self.assertIn("String too short", error_msg)
        self.assertIn("Value must be greater than 0", error_msg)
        self.assertIn("body -> name", error_msg)
        self.assertIn("query -> limit", error_msg)

    def test_handle_validation_errors_decorator_catches_422(self):
        """Test that the decorator catches UnprocessableEntityException."""
        # Create a mock HTTP response
        mock_http_resp = Mock()
        mock_http_resp.status = 422
        mock_http_resp.reason = "Unprocessable Entity"
        mock_http_resp.data = b'{"detail": []}'
        mock_http_resp.getheaders.return_value = {}

        # Create error JSON
        error_json = {
            "detail": [
                {
                    "loc": ["body", "code"],
                    "msg": "Field required",
                    "type": "value_error.missing",
                }
            ]
        }
        error_json_str = json.dumps(error_json)

        # Create UnprocessableEntityException
        original_exc = UnprocessableEntityException(http_resp=mock_http_resp, body=error_json_str, data=None)

        # Create a function that raises the exception
        @handle_validation_errors
        def failing_function():
            raise original_exc

        # Verify that ValidationException is raised
        with self.assertRaises(ValidationException) as ctx:
            failing_function()

        # Verify the exception has the parsed error
        exc = ctx.exception
        self.assertIsNotNone(exc.validation_error)
        self.assertIsNotNone(exc.validation_error.detail)
        assert exc.validation_error.detail is not None  # Type narrowing for basedpyright
        self.assertEqual(len(exc.validation_error.detail), 1)
        self.assertEqual(exc.validation_error.detail[0].msg, "Field required")

    def test_handle_validation_errors_decorator_passes_through_success(self):
        """Test that the decorator doesn't interfere with successful calls."""

        @handle_validation_errors
        def successful_function():
            return "success"

        result = successful_function()
        self.assertEqual(result, "success")

    def test_handle_validation_errors_decorator_with_malformed_json(self):
        """Test that the decorator handles malformed JSON gracefully."""
        # Create a mock HTTP response with invalid JSON
        mock_http_resp = Mock()
        mock_http_resp.status = 422
        mock_http_resp.reason = "Unprocessable Entity"
        mock_http_resp.data = b"not valid json"
        mock_http_resp.getheaders.return_value = {}

        original_exc = UnprocessableEntityException(http_resp=mock_http_resp, body="not valid json", data=None)

        @handle_validation_errors
        def failing_function():
            raise original_exc

        # Should still raise ValidationException even with malformed JSON
        with self.assertRaises(ValidationException) as ctx:
            failing_function()

        # The exception should have a validation_error but with no detail
        exc = ctx.exception
        self.assertIsNotNone(exc.validation_error)

    def test_validation_exception_repr(self):
        """Test ValidationException __repr__ method."""
        loc_inner = ValidationErrorLocInner(actual_instance="body")
        error1 = ValidationError(loc=[loc_inner], msg="Error 1", type="value_error")
        error2 = ValidationError(loc=[loc_inner], msg="Error 2", type="value_error")
        http_error = HTTPValidationError(detail=[error1, error2])

        exc = ValidationException(http_error, Exception("original"))
        self.assertEqual(repr(exc), "ValidationException(errors=2)")

    def test_validation_exception_no_details(self):
        """Test ValidationException with no error details."""
        http_error = HTTPValidationError(detail=None)
        exc = ValidationException(http_error, Exception("original"))

        error_msg = str(exc)
        self.assertIn("no details available", error_msg)


if __name__ == "__main__":
    _ = unittest.main()
