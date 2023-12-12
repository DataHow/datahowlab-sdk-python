"""Authentication module for DHL SDK

This module provides functionality for handling 
API Key Authentication. It allows you to securely 
manage and use API keys for authenticating requests 
to the DataHowLab API. 

The module includes a class, `APIKeyAuthentication`, that can
be used to obtain and include API Key authorization headers in 
your requests. It also offers the flexibility to either pass 
an API key as an argument or retrieve it from environment variables.

Classes:
    - APIKeyAuthentication: Manages API Key authentication and provides 
      methods for generating authorization headers using the API Key.

Usage:
    To use this module, create an instance of the `APIKeyAuthentication`
    class, passing an API key as an argument or allowing it 
    to retrieve the API key from environment variables. 
    You can then call the `get_headers` method to obtain the authorization 
    headers, which can be added to your requests.

"""

import os
from typing import Optional


class APIKeyAuthentication:
    # pylint: disable=too-few-public-methods
    """
    API Key Authentication

    The API Key can be provided as an argument or retrieved from the
    environment variable defined as 'DHL_API_KEY'
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Parameters
        ----------
        api_key : str, optional
            API Key to use to authenticate with the DHL API

        Returns
        -------
        NoneType
            None
        """
        self.api_key = self._get_api_key(api_key)

    def get_headers(self) -> dict[str, str]:
        """Get the authorization headers to add to the
        requests using the API Key.

        Returns
        -------
        dict
            Authorization Headers for the request to the API
        """
        return {"Authorization": f"ApiKey {self.api_key}"}

    def _get_api_key(self, api_key: Optional[str] = None) -> str:
        """Get the API Key from the environment variables
        if not given.

        Parameters
        ----------
        api_key : str, optional
            API Key to use, by default None

        Returns
        -------
        str
            API Key
        """

        if api_key is None:
            api_key = os.environ.get("DHL_API_KEY", None)

        if api_key is None:
            raise KeyError("DHL API Key not found")

        return api_key
