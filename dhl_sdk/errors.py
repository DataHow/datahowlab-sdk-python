"""Exception hierarchy for DHL SDK

This module provides structured exceptions for better error handling.
All exceptions include error codes and optional details for programmatic handling.
"""

from typing import Any


class DHLError(Exception):
    """Base exception for all DHL SDK errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional error context as dictionary
    """

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class ValidationError(DHLError):
    """Raised when input validation fails.

    Examples:
        >>> raise ValidationError("Code must be 1-10 characters", field="code", value="")
    """

    def __init__(self, message: str, field: str, value: Any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": value},
        )
        self.field = field
        self.value = value


class EntityNotFoundError(DHLError):
    """Raised when attempting to access an entity that doesn't exist.

    Examples:
        >>> raise EntityNotFoundError("Product not found", entity_type="Product", entity_id="123")
    """

    def __init__(self, message: str, entity_type: str, entity_id: str | None = None):
        details = {"entity_type": entity_type}
        if entity_id is not None:
            details["entity_id"] = entity_id

        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            details=details,
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class EntityAlreadyExistsError(DHLError):
    """Raised when attempting to create an entity that already exists.

    Examples:
        >>> raise EntityAlreadyExistsError("Product already exists", entity_type="Product", entity_identifier="PROD")
    """

    def __init__(
        self,
        message: str,
        entity_type: str,
        entity_identifier: str | None = None,
    ):
        details = {"entity_type": entity_type}
        if entity_identifier is not None:
            details["entity_identifier"] = entity_identifier

        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS",
            details=details,
        )
        self.entity_type = entity_type
        self.entity_identifier = entity_identifier


class PredictionError(DHLError):
    """Raised when model prediction fails.

    Examples:
        >>> raise PredictionError("Prediction failed", model_id="123")
        >>> raise PredictionError("Invalid input dimensions", details={"expected": 100, "got": 50})
    """

    def __init__(
        self,
        message: str,
        model_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        error_details = details or {}
        if model_id is not None:
            error_details["model_id"] = model_id

        super().__init__(
            message=message, code="PREDICTION_ERROR", details=error_details
        )
        self.model_id = model_id


class AuthenticationError(DHLError):
    """Raised when authentication fails (HTTP 401).

    Examples:
        >>> raise AuthenticationError("Invalid API key")
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message=message, code="AUTHENTICATION_ERROR", details=details)


class PermissionDeniedError(DHLError):
    """Raised when access is forbidden (HTTP 403).

    Examples:
        >>> raise PermissionDeniedError("Insufficient permissions to access resource")
    """

    def __init__(
        self,
        message: str = "Permission denied",
        resource: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        error_details = details or {}
        if resource:
            error_details["resource"] = resource

        super().__init__(
            message=message, code="PERMISSION_DENIED", details=error_details
        )
        self.resource = resource


class RateLimitError(DHLError):
    """Raised when rate limit is exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header)

    Examples:
        >>> raise RateLimitError("Rate limit exceeded", retry_after=60)
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        error_details = details or {}
        if retry_after is not None:
            error_details["retry_after"] = retry_after

        super().__init__(
            message=message, code="RATE_LIMIT_EXCEEDED", details=error_details
        )
        self.retry_after = retry_after


class ServerError(DHLError):
    """Raised when server encounters an error (HTTP 5xx).

    Examples:
        >>> raise ServerError("Internal server error", status_code=500)
    """

    def __init__(
        self,
        message: str = "Server error",
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        error_details = details or {}
        if status_code is not None:
            error_details["status_code"] = status_code

        super().__init__(message=message, code="SERVER_ERROR", details=error_details)
        self.status_code = status_code


class APIError(DHLError):
    """Raised when API request fails.

    Attributes:
        status_code: HTTP status code
        response_body: Raw response body

    Examples:
        >>> raise APIError("Request failed", status_code=500, response_body="...")
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any | None = None,
    ):
        details = {}
        if status_code is not None:
            details["status_code"] = status_code
        if response_body is not None:
            details["response_body"] = response_body

        super().__init__(message=message, code="API_ERROR", details=details)
        self.status_code = status_code
        self.response_body = response_body
