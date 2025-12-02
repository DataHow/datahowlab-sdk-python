# Disable import cycle check: __init__ imports client which imports entities which may import client
# (those are only relevant for type checking)
# pyright: reportImportCycles=false
"""DHL SDK for Python"""

__all__ = [
    "APIKeyAuthentication",
    "DataHowLabClient",
    "ValidationException",
    "convert_tags_for_openapi",
]

from urllib.parse import quote
import json


def _patch_openapi_deepobject_serialization() -> None:
    """
    Monkey patch the OpenAPI client to properly handle deepObject parameters.

    The OpenAPI generator has a known bug where it incorrectly handles deepObject
    style parameters (style=deepObject, explode=true in OpenAPI spec). It generates
    Dict[str, Dict[str, str]] type but then JSON-encodes the entire dict as a single
    query parameter value instead of expanding it to the correct format: param[key]=value.

    This patch fixes the parameters_to_url_query method to properly serialize
    deepObject parameters according to the OpenAPI 3.x specification.

    Related OpenAPI Generator Issues:
    - https://github.com/OpenAPITools/openapi-generator/issues/9603
      "[BUG][Python] deepObject parameter style creates invalid code"
    - https://github.com/OpenAPITools/openapi-generator/issues/7837
      "[BUG] [python-flask] deepObjects in query causes exception"

    See Also:
    - OpenAPI 3.0 Spec on Parameter Serialization:
      https://swagger.io/docs/specification/serialization/
    """
    from openapi_client.api_client import ApiClient

    # Save reference to original method (not used but good practice)
    _original_parameters_to_url_query = ApiClient.parameters_to_url_query  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType] - Runtime patching

    def fixed_parameters_to_url_query(self, params, collection_formats):  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType, reportUnusedParameter] - Matching OpenAPI signature
        """
        Fixed version that handles deepObject parameters (tags) correctly.

        Converts: tags={'key': {'key': 'value'}}
        To URL: tags[key]=value

        Parameters
        ----------
        params : dict or list of tuples
            Parameters to serialize
        collection_formats : dict
            Parameter collection formats

        Returns
        -------
        str
            URL query string
        """
        new_params: list[tuple[str, str]] = []
        if collection_formats is None:
            collection_formats = {}

        for k, v in params.items() if isinstance(params, dict) else params:  # pyright: ignore[reportUnknownVariableType] - Dynamic dict iteration
            # Special handling for 'tags' parameter (deepObject style)
            # OpenAPI spec defines it as style=deepObject, explode=true
            if k == "tags" and isinstance(v, dict):
                # Flatten nested dict to deepObject format
                # Expected structure: {'outer_key': {'inner_key': 'value'}}
                # Output format: tags[outer_key]=value
                for outer_key, inner_dict in v.items():  # pyright: ignore[reportUnknownVariableType] - Dynamic dict iteration
                    if isinstance(inner_dict, dict):
                        # Use the first (and should be only) inner value
                        for inner_key, inner_value in inner_dict.items():  # pyright: ignore[reportUnknownVariableType, reportUnusedVariable] - Need to iterate for dict values
                            param_name = f"{k}[{outer_key}]"
                            new_params.append((param_name, quote(str(inner_value))))  # pyright: ignore[reportUnknownArgumentType] - str() handles any type
                            break  # Only use first inner value
                    else:
                        # Fallback: treat as simple value
                        param_name = f"{k}[{outer_key}]"
                        new_params.append((param_name, quote(str(inner_dict))))  # pyright: ignore[reportUnknownArgumentType] - str() handles any type
                continue

            # Original logic for all other parameters
            if isinstance(v, bool):
                v = str(v).lower()
            if isinstance(v, (int, float)):
                v = str(v)
            if isinstance(v, dict):
                v = json.dumps(v)

            if k in collection_formats:
                collection_format = collection_formats[k]  # pyright: ignore[reportUnknownVariableType] - Dynamic dict access
                if collection_format == "multi":
                    new_params.extend((k, quote(str(value))) for value in v)
                else:
                    if collection_format == "ssv":
                        delimiter = " "
                    elif collection_format == "tsv":
                        delimiter = "\t"
                    elif collection_format == "pipes":
                        delimiter = "|"
                    else:  # csv is the default
                        delimiter = ","
                    new_params.append((k, delimiter.join(quote(str(value)) for value in v)))  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType] - str() handles any type
            else:
                new_params.append((k, quote(str(v))))  # pyright: ignore[reportUnknownArgumentType] - str() handles any type

        return "&".join(["=".join(map(str, item)) for item in new_params])

    # Apply the patch
    ApiClient.parameters_to_url_query = fixed_parameters_to_url_query


def convert_tags_for_openapi(tags: dict[str, str] | None) -> dict[str, dict[str, str]] | None:
    """
    Convert simple tag dict to nested format required by OpenAPI generator bug.

    The OpenAPI generator incorrectly expects Dict[str, Dict[str, StrictStr]]
    for deepObject parameters due to bugs in handling the OpenAPI 3.x deepObject
    style specification. We convert the user-friendly format to what the generator
    expects, which is then properly serialized by our monkey patch.

    This conversion, combined with the monkey patch in _patch_openapi_deepobject_serialization(),
    results in the correct URL format: tags[key]=value

    Parameters
    ----------
    tags : dict[str, str] | None
        Simple key-value tag dictionary (e.g., {"sdk-example": "true"})

    Returns
    -------
    dict[str, dict[str, str]] | None
        Nested dictionary format expected by OpenAPI generator
        (e.g., {"sdk-example": {"sdk-example": "true"}})

    Examples
    --------
    >>> convert_tags_for_openapi({"sdk-example": "true"})
    {"sdk-example": {"sdk-example": "true"}}
    >>> convert_tags_for_openapi(None)
    None

    See Also
    --------
    _patch_openapi_deepobject_serialization : The monkey patch that handles serialization
    https://github.com/OpenAPITools/openapi-generator/issues/9603 : Related bug report
    """
    if tags is None:
        return None
    return {key: {key: value} for key, value in tags.items()}


# Apply the patch when the module is imported
_patch_openapi_deepobject_serialization()

# Import after patching to ensure patch is applied before any API usage
from dhl_sdk.authentication import APIKeyAuthentication  # noqa: E402
from dhl_sdk.client import DataHowLabClient  # noqa: E402
from dhl_sdk.exceptions import ValidationException  # noqa: E402
