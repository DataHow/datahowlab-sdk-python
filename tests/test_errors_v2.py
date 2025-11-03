"""Unit tests for dhl_sdk.errors module."""

import pytest

from dhl_sdk.errors import (
    APIError,
    AuthenticationError,
    DHLError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PredictionError,
    ValidationError,
)

# =============================================================================
# Base Error Tests
# =============================================================================


def test_dhl_error_creation():
    """Test DHLError base class creation."""
    error = DHLError(message="Test error", code="TEST_ERROR", details={"key": "value"})
    assert str(error) == "Test error"
    assert error.code == "TEST_ERROR"
    assert error.details == {"key": "value"}


def test_dhl_error_defaults():
    """Test DHLError default values."""
    error = DHLError(message="Test error")
    assert error.code == "UNKNOWN_ERROR"
    assert error.details == {}


def test_dhl_error_string_representation():
    """Test DHLError string representation."""
    error = DHLError(message="Something went wrong")
    assert str(error) == "Something went wrong"


# =============================================================================
# ValidationError Tests
# =============================================================================


def test_validation_error_creation():
    """Test ValidationError creation."""
    error = ValidationError(message="Invalid value", field="code", value="")
    assert str(error) == "Invalid value"
    assert error.code == "VALIDATION_ERROR"
    assert error.field == "code"
    assert error.value == ""
    assert error.details["field"] == "code"
    assert error.details["value"] == ""


def test_validation_error_without_value():
    """Test ValidationError without value parameter."""
    error = ValidationError(message="Field is required", field="name")
    assert error.field == "name"
    assert error.value is None
    assert "field" in error.details


def test_validation_error_inheritance():
    """Test that ValidationError is a DHLError."""
    error = ValidationError(message="Test", field="test")
    assert isinstance(error, DHLError)
    assert isinstance(error, ValidationError)


# =============================================================================
# EntityNotFoundError Tests
# =============================================================================


def test_entity_not_found_error_creation():
    """Test EntityNotFoundError creation."""
    error = EntityNotFoundError(
        message="Product not found", entity_type="Product", entity_id="prod-123"
    )
    assert str(error) == "Product not found"
    assert error.code == "ENTITY_NOT_FOUND"
    assert error.entity_type == "Product"
    assert error.entity_id == "prod-123"
    assert error.details["entity_type"] == "Product"
    assert error.details["entity_id"] == "prod-123"


def test_entity_not_found_error_without_id():
    """Test EntityNotFoundError without entity_id."""
    error = EntityNotFoundError(message="Variable not found", entity_type="Variable")
    assert error.entity_type == "Variable"
    assert error.entity_id is None
    assert "entity_type" in error.details


def test_entity_not_found_error_inheritance():
    """Test that EntityNotFoundError is a DHLError."""
    error = EntityNotFoundError(message="Not found", entity_type="Test")
    assert isinstance(error, DHLError)
    assert isinstance(error, EntityNotFoundError)


# =============================================================================
# EntityAlreadyExistsError Tests
# =============================================================================


def test_entity_already_exists_error_creation():
    """Test EntityAlreadyExistsError creation."""
    error = EntityAlreadyExistsError(
        message="Product already exists",
        entity_type="Product",
        entity_identifier="PROD1",
    )
    assert str(error) == "Product already exists"
    assert error.code == "ENTITY_ALREADY_EXISTS"
    assert error.entity_type == "Product"
    assert error.entity_identifier == "PROD1"
    assert error.details["entity_type"] == "Product"
    assert error.details["entity_identifier"] == "PROD1"


def test_entity_already_exists_error_without_identifier():
    """Test EntityAlreadyExistsError without entity_identifier."""
    error = EntityAlreadyExistsError(
        message="Variable already exists", entity_type="Variable"
    )
    assert error.entity_type == "Variable"
    assert error.entity_identifier is None
    assert "entity_type" in error.details


def test_entity_already_exists_error_inheritance():
    """Test that EntityAlreadyExistsError is a DHLError."""
    error = EntityAlreadyExistsError(message="Already exists", entity_type="Test")
    assert isinstance(error, DHLError)
    assert isinstance(error, EntityAlreadyExistsError)


# =============================================================================
# PredictionError Tests
# =============================================================================


def test_prediction_error_creation():
    """Test PredictionError creation."""
    error = PredictionError(
        message="Prediction failed",
        model_id="model-123",
        details={"reason": "Invalid input dimensions"},
    )
    assert str(error) == "Prediction failed"
    assert error.code == "PREDICTION_ERROR"
    assert error.model_id == "model-123"
    assert error.details["model_id"] == "model-123"
    assert error.details["reason"] == "Invalid input dimensions"


def test_prediction_error_without_model_id():
    """Test PredictionError without model_id."""
    error = PredictionError(message="Prediction failed")
    assert error.model_id is None


def test_prediction_error_with_custom_details():
    """Test PredictionError with custom details dict."""
    custom_details = {"error_type": "dimension_mismatch", "expected": 100, "got": 50}
    error = PredictionError(
        message="Dimension mismatch",
        model_id="model-456",
        details=custom_details,
    )
    assert error.details["error_type"] == "dimension_mismatch"
    assert error.details["expected"] == 100
    assert error.details["model_id"] == "model-456"


def test_prediction_error_inheritance():
    """Test that PredictionError is a DHLError."""
    error = PredictionError(message="Failed")
    assert isinstance(error, DHLError)
    assert isinstance(error, PredictionError)


# =============================================================================
# APIError Tests
# =============================================================================


def test_api_error_creation():
    """Test APIError creation."""
    error = APIError(
        message="Server error",
        status_code=500,
        response_body={"error": "Internal server error"},
    )
    assert str(error) == "Server error"
    assert error.code == "API_ERROR"
    assert error.status_code == 500
    assert error.response_body == {"error": "Internal server error"}
    assert error.details["status_code"] == 500
    assert error.details["response_body"] == {"error": "Internal server error"}


def test_api_error_without_response_body():
    """Test APIError without response_body."""
    error = APIError(message="Bad request", status_code=400)
    assert error.status_code == 400
    assert error.response_body is None
    assert "status_code" in error.details


def test_api_error_with_string_response():
    """Test APIError with string response body."""
    error = APIError(
        message="Server error", status_code=500, response_body="Internal server error"
    )
    assert error.response_body == "Internal server error"
    assert error.details["response_body"] == "Internal server error"


def test_api_error_inheritance():
    """Test that APIError is a DHLError."""
    error = APIError(message="Error", status_code=500)
    assert isinstance(error, DHLError)
    assert isinstance(error, APIError)


# =============================================================================
# AuthenticationError Tests
# =============================================================================


def test_authentication_error_creation():
    """Test AuthenticationError creation."""
    error = AuthenticationError(message="Invalid API key")
    assert str(error) == "Invalid API key"
    assert error.code == "AUTHENTICATION_ERROR"


def test_authentication_error_with_details():
    """Test AuthenticationError with custom details."""
    error = AuthenticationError(
        message="Authentication failed", details={"reason": "Token expired"}
    )
    assert error.details["reason"] == "Token expired"


def test_authentication_error_inheritance():
    """Test that AuthenticationError is a DHLError."""
    error = AuthenticationError(message="Unauthorized")
    assert isinstance(error, DHLError)
    assert isinstance(error, AuthenticationError)


# =============================================================================
# Error Hierarchy Tests
# =============================================================================


def test_all_errors_inherit_from_dhl_error():
    """Test that all error classes inherit from DHLError."""
    error_classes = [
        ValidationError,
        EntityNotFoundError,
        EntityAlreadyExistsError,
        PredictionError,
        APIError,
        AuthenticationError,
    ]

    for error_class in error_classes:
        assert issubclass(error_class, DHLError)


def test_all_errors_inherit_from_exception():
    """Test that all error classes inherit from Exception."""
    error_classes = [
        DHLError,
        ValidationError,
        EntityNotFoundError,
        EntityAlreadyExistsError,
        PredictionError,
        APIError,
        AuthenticationError,
    ]

    for error_class in error_classes:
        assert issubclass(error_class, Exception)


# =============================================================================
# Error Catching Tests
# =============================================================================


def test_catch_specific_error():
    """Test catching specific error types."""
    try:
        raise ValidationError(message="Invalid", field="test")
    except ValidationError as e:
        assert e.field == "test"


def test_catch_base_error():
    """Test catching DHLError catches all custom errors."""
    for error_class in [
        ValidationError,
        EntityNotFoundError,
        EntityAlreadyExistsError,
        PredictionError,
        APIError,
        AuthenticationError,
    ]:
        try:
            if error_class == ValidationError:
                raise error_class(message="Test", field="test")
            elif error_class in [EntityNotFoundError, EntityAlreadyExistsError]:
                raise error_class(message="Test", entity_type="Test")
            elif error_class == APIError:
                raise error_class(message="Test", status_code=500)
            else:
                raise error_class(message="Test")
        except DHLError as e:
            assert isinstance(e, error_class)


def test_catch_as_exception():
    """Test catching errors as generic Exception."""
    try:
        raise ValidationError(message="Test", field="test")
    except Exception as e:
        assert isinstance(e, ValidationError)
        assert isinstance(e, DHLError)


# =============================================================================
# Error Message Tests
# =============================================================================


def test_error_messages_are_descriptive():
    """Test that error messages are preserved correctly."""
    messages = [
        "Product code cannot be empty",
        "Experiment 'exp-123' not found",
        "Variable with code 'TEMP' already exists",
        "Model prediction failed due to invalid input dimensions",
        "API request failed with status 500",
        "Invalid API key provided",
    ]

    errors = [
        ValidationError(message=messages[0], field="code"),
        EntityNotFoundError(message=messages[1], entity_type="Experiment"),
        EntityAlreadyExistsError(message=messages[2], entity_type="Variable"),
        PredictionError(message=messages[3]),
        APIError(message=messages[4], status_code=500),
        AuthenticationError(message=messages[5]),
    ]

    for i, error in enumerate(errors):
        assert str(error) == messages[i]


# =============================================================================
# Error Details Tests
# =============================================================================


def test_error_details_are_accessible():
    """Test that error details are properly stored and accessible."""
    error = ValidationError(message="Invalid", field="code", value="")
    assert error.details["field"] == "code"
    assert error.details["value"] == ""

    error2 = EntityNotFoundError(
        message="Not found", entity_type="Product", entity_id="prod-123"
    )
    assert error2.details["entity_type"] == "Product"
    assert error2.details["entity_id"] == "prod-123"

    error3 = APIError(
        message="Error", status_code=404, response_body={"message": "Not found"}
    )
    assert error3.details["status_code"] == 404
    assert error3.details["response_body"]["message"] == "Not found"


def test_error_details_are_mutable():
    """Test that error details can be updated after creation."""
    error = DHLError(message="Test", details={"key1": "value1"})
    error.details["key2"] = "value2"
    assert error.details["key1"] == "value1"
    assert error.details["key2"] == "value2"


# =============================================================================
# Error Code Tests
# =============================================================================


def test_error_codes_are_unique():
    """Test that each error type has a unique code."""
    errors = [
        DHLError(message="Test"),
        ValidationError(message="Test", field="test"),
        EntityNotFoundError(message="Test", entity_type="Test"),
        EntityAlreadyExistsError(message="Test", entity_type="Test"),
        PredictionError(message="Test"),
        APIError(message="Test", status_code=500),
        AuthenticationError(message="Test"),
    ]

    codes = [e.code for e in errors]
    assert len(codes) == len(set(codes))  # All codes are unique


def test_error_codes_are_uppercase():
    """Test that error codes are uppercase."""
    errors = [
        DHLError(message="Test"),
        ValidationError(message="Test", field="test"),
        EntityNotFoundError(message="Test", entity_type="Test"),
        EntityAlreadyExistsError(message="Test", entity_type="Test"),
        PredictionError(message="Test"),
        APIError(message="Test", status_code=500),
        AuthenticationError(message="Test"),
    ]

    for error in errors:
        assert error.code == error.code.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
