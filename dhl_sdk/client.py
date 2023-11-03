"""Cliente for the DHL SpectraHow API

This module defines the `Client` and `SpectraHowClient` classes, 
which are used to interact with the DHL SpectraHow API.

Classes:
    - Client: provides a base implementation for making HTTP requests to the API, 
    - SpectraHowClient: extends 'Client' class with additional methods for specific
      Spectra projects.

"""


from typing import Optional, Dict, Any
from urllib.parse import urlencode

from requests import Response
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter

from dhl_sdk.authentication import APIKeyAuthentication

from dhl_sdk.crud import Result
from dhl_sdk.entities import Project
from dhl_sdk._utils import urljoin


SPECTRA_UNIT_ID = "373c173a-1f23-4e56-874e-90ca4702ec0d"


class Client:
    """
    A client for interacting with the DataHowLab API.

    Parameters
    ----------
    auth_key : APIKeyAuthentication
        An instance of the APIKeyAuthentication class containing the user's API key.
    base_url : str
        The URL address of the datahowlab application
    """

    def __init__(self, auth_key: APIKeyAuthentication, base_url: str):
        self.auth_key = auth_key
        self.base_url = base_url
        self.session = Client._get_retry_requester(total_retries=5, backoff_factor=1)

    @staticmethod
    def _get_retry_requester(total_retries=5, backoff_factor=1):
        """Get the http session with retry strategy"""
        status_forcelist = [429, 502, 503, 504]
        allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE"]

        retry_strategy = Retry(
            total=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=allowed_methods,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        return http

    def post(self, path: str, json_data: Any) -> Response:
        """
        Sends a POST request to the specified
        URL with the provided JSON data as a dict.

        Parameters
        ----------
        path : str
            The extension to send the POST request to.
        json_data : any
            The JSON data to include in the POST request.

        Returns
        -------
        requests.Response
            The response object returned by the server.

        Raises
        ------
        requests.exceptions.HTTPError
            If the server returns a non-2xx status code.
        """
        path = urljoin(self.base_url, path)
        auth_headers = self.auth_key.get_headers()

        response = self.session.post(path, headers=auth_headers, json=json_data)
        response.raise_for_status()

        return response

    def get(self, path: str, query_params: Optional[Dict[str, str]] = None) -> Response:
        """
        Sends a GET request to the specified URL
        with the given query parameters.

        Parameters:
        -----------
        path : str
            The URL to send the GET request to.
        query_params : dict, optional
            A dictionary of query parameters to include in the request.

        Returns:
        --------
        response : requests.Response
            The response object returned by the GET request.

        Raises:
        -------
        requests.exceptions.HTTPError
            If the server returns a non-2xx status code.
        """
        if query_params:
            query_string = urlencode(query_params, doseq=True, safe="[]")
            path = f"{path}?{query_string}"

        path = urljoin(self.base_url, path)
        auth_headers = self.auth_key.get_headers()

        response = self.session.get(path, headers=auth_headers)
        response.raise_for_status()

        return response

    def get_projects(
        self,
        name: str = None,
        unit_id: str = None,
        offset: int = 0,
    ) -> Result[Project]:
        """Retrieve the available projects for the user

        Parameters
        ----------
        name : str, optional
            Filter projects by name, by default None
        unit_id : str, optional
            Filter projects by process unit ID, by default None
        offset : int, optional
            The offset for pagination, must be a non-negative integer, by default 0

        Returns
        -------
        Result
            An Iterable object containing the retrieved project data
        """

        if not (isinstance(offset, int) and offset >= 0):
            raise ValueError("offset must be a non-negative integer")

        filter_params = {
            key: value
            for key, value in {
                "filterBy[processUnitId]": unit_id,
                "filterBy[name]": name,
            }.items()
            if value is not None
        }

        projects = Project.requests(self)
        result = Result[Project](
            offset=offset,
            limit=10,
            query_params=filter_params,
            requests=projects,
        )

        return result


class SpectraHowClient:
    """Client for the DHL SpectraHow API

    Parameters
    ----------
    auth_key : APIKeyAuthentication
        An instance of the APIKeyAuthentication class containing the user's API key."""

    def __init__(self, auth_key: APIKeyAuthentication, base_url: str):
        self._client = Client(auth_key, base_url)

    def get_projects(
        self,
        name: str = None,
        offset: int = 0,
    ) -> Result[Project]:
        """
        Retrieves an iterable of Spectra projects from the DHL API.

        Parameters
        ----------
        name : str, optional
            A string to filter projects by name.
        offset : int, optional
            An integer representing the number of projects to skip before returning results.

        Returns
        -------
        Result
            An Iterable object containing the retrieved projects
        """

        return self._client.get_projects(
            name=name,
            offset=offset,
            unit_id=SPECTRA_UNIT_ID,
        )
