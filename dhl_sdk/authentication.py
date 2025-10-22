"""Authentication module for DHL SDK

This module provides functionality for handling
API Key Authentication. It allows you to securely
manage and use API keys for authenticating requests
to the DataHowLab API.

The module includes a class, `APIKeyAuthentication`, that can
be used to store your API Key and generate authorization headers.
It offers the flexibility to either pass an API key as an argument
or retrieve it from environment variables.

Classes:
    - APIKeyAuthentication: Manages API Key authentication and provides
      methods for generating authorization headers using the API Key.

Usage:
    To use this module, create an instance of the `APIKeyAuthentication`
    class, passing an API key as an argument or allowing it
    to retrieve the API key from environment variables.
    You can then access the `api_key` attribute directly or call the
    `get_headers` method to obtain the authorization headers, which can
    be added to your requests.

"""

import os


class APIKeyAuthentication:
    """
    API Key Authentication

    The API Key can be provided as an argument or retrieved from the
    environment variable 'DHL_API_KEY'.
    """

    api_key: str

    def __init__(self, api_key: str | None = None):
        """
        Parameters
        ----------
        api_key : str, optional
            API Key to authenticate with the DHL API.
            If not provided, will be read from DHL_API_KEY environment variable.

        Raises
        ------
        KeyError
            If no API key is provided and DHL_API_KEY environment variable is not set.
        """
        if api_key is None:
            api_key = os.environ.get("DHL_API_KEY")

        if api_key is None:
            raise KeyError("DHL API Key not found. Provide api_key parameter or set DHL_API_KEY environment variable.")

        self.api_key = api_key

    def get_headers(self) -> dict[str, str]:
        """Get the authorization headers for API requests.

        Returns
        -------
        dict[str, str]
            Authorization headers with API Key
        """
        return {"Authorization": f"ApiKey {self.api_key}"}
