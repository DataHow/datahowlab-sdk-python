"""Error handling utilities for wrapping OpenAPI client exceptions."""

import json
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

from openapi_client.exceptions import UnprocessableEntityException
from openapi_client.models.http_validation_error import HTTPValidationError

from dhl_sdk.exceptions import ValidationException

P = ParamSpec("P")
T = TypeVar("T")


def handle_validation_errors(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that catches UnprocessableEntityException and converts it to ValidationException.

    This decorator wraps API calls that may return 422 validation errors, parsing
    the response body into a strongly-typed HTTPValidationError Pydantic model
    and re-throwing as a ValidationException.

    Parameters
    ----------
    func : Callable
        The function to wrap (typically an API call)

    Returns
    -------
    Callable
        Wrapped function that converts 422 errors to ValidationException

    Example
    -------
    >>> @handle_validation_errors
    ... def create_variable(api, data):
    ...     return api.create_variable_api_v1_variables_post(variable_create=data)
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except UnprocessableEntityException as e:
            # Try to parse the response body as HTTPValidationError
            validation_error = None

            if e.body:  # pyright: ignore[reportUnknownMemberType]
                try:
                    # Parse JSON string to HTTPValidationError Pydantic model
                    validation_error = HTTPValidationError.from_json(e.body)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                except (json.JSONDecodeError, ValueError, Exception):
                    # If parsing fails, we'll still raise ValidationException
                    # but with None validation_error (will show generic message)
                    pass

            # If we couldn't parse the body, try to create a basic error structure
            if validation_error is None:
                try:
                    # Create a minimal HTTPValidationError
                    validation_error = HTTPValidationError(detail=None)
                except Exception:
                    # Last resort: create empty error
                    validation_error = HTTPValidationError()

            # Raise our custom ValidationException with parsed data
            raise ValidationException(validation_error, e) from e

    return wrapper
