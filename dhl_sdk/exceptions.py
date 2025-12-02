"""Custom exceptions for the DataHowLab SDK."""

from typing import TYPE_CHECKING
from typing_extensions import override

if TYPE_CHECKING:
    from openapi_client.models.http_validation_error import HTTPValidationError


class ValidationException(Exception):
    """
    Exception raised when API validation fails (HTTP 422).

    This exception wraps the HTTPValidationError returned by the API
    and provides easy access to validation error details.

    Attributes
    ----------
    validation_error : HTTPValidationError
        The parsed validation error from the API containing detailed
        information about what went wrong.
    original_exception : Exception
        The original UnprocessableEntityException from the OpenAPI client.

    Example
    -------
    >>> try:
    ...     variable_request.create(client)
    ... except ValidationException as e:
    ...     print(f"Validation failed: {e}")
    ...     if e.validation_error and e.validation_error.detail:
    ...         for error in e.validation_error.detail:
    ...             print(f"  - {error.loc}: {error.msg} ({error.type})")
    """

    validation_error: "HTTPValidationError"
    original_exception: Exception

    def __init__(self, validation_error: "HTTPValidationError", original_exception: Exception):
        """
        Initialize ValidationException.

        Parameters
        ----------
        validation_error : HTTPValidationError
            Parsed validation error from API response
        original_exception : Exception
            Original exception from OpenAPI client
        """
        self.validation_error = validation_error
        self.original_exception = original_exception
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format a human-readable error message from validation errors."""
        if not self.validation_error or not self.validation_error.detail:
            return "API validation failed (no details available)"

        messages = ["API validation failed:"]
        for error in self.validation_error.detail:
            # Format location path
            loc_parts = []
            for loc_item in error.loc:
                # ValidationErrorLocInner can be string or int
                actual = loc_item.actual_instance
                loc_parts.append(str(actual))  # pyright: ignore[reportUnknownMemberType]
            location = " -> ".join(loc_parts) if loc_parts else "unknown"  # pyright: ignore[reportUnknownArgumentType]

            messages.append(f"  [{location}] {error.msg} (type: {error.type})")

        return "\n".join(messages)

    @override
    def __str__(self) -> str:
        """Return formatted error message."""
        return self._format_message()

    @override
    def __repr__(self) -> str:
        """Return representation of the exception."""
        error_count = len(self.validation_error.detail) if self.validation_error and self.validation_error.detail else 0
        return f"ValidationException(errors={error_count})"
