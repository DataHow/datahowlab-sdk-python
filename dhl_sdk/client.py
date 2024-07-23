# pylint: disable=too-few-public-methods

"""Client for the DHL SpectraHow API

This module defines the `Client` and `DataHowLabClient` classes, 
which are used to interact with the DataHowLab's API.

Classes:
    - Client: provides a base implementation for making HTTP requests to the API
    - DataHowLabClient: main client to interact with the DHL API
"""

from typing import Any, Dict, Literal, Optional, Type, TypeVar, Union
from urllib.parse import urlencode

import requests
from requests import Response
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util.retry import Retry

from dhl_sdk._utils import VariableGroupCodes, urljoin
from dhl_sdk.authentication import APIKeyAuthentication
from dhl_sdk.crud import Result
from dhl_sdk.db_entities import DataBaseEntity, Experiment, Product, Recipe
from dhl_sdk.entities import CultivationProject, Project, SpectraProject, Variable

PROJECT_TYPE_MAP = {
    "cultivation": ("04a324da-13a5-470b-94a1-bda6ac87bb86", CultivationProject),
    "spectroscopy": ("373c173a-1f23-4e56-874e-90ca4702ec0d", SpectraProject),
}


T = TypeVar("T", bound=Project)


class Client:
    """
    A client for interacting with the DataHowLab API.
    """

    def __init__(
        self, auth_key: APIKeyAuthentication, base_url: str, verify: bool = True
    ) -> None:
        """
        Parameters
        ----------
        auth_key : APIKeyAuthentication
            An instance of the APIKeyAuthentication class containing the user's API key.
        base_url : str
            The URL address of the datahowlab application

        Returns
        -------
        NoneType
            None
        """
        self.auth_key = auth_key
        self.base_url = base_url
        self.session = Client._get_retry_requester(
            total_retries=5, backoff_factor=1, verify=verify
        )

    @staticmethod
    def _get_retry_requester(
        total_retries: int = 5, backoff_factor: int = 1, verify: int = True
    ):
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
        http.verify = verify
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

    def put(
        self,
        path: str,
        data: Any,
        content_type: Literal["application/json", "text/csv"] = "application/json",
    ) -> Response:
        """
        Sends a PUT request to the specified
        URL with the provided JSON data as a dict.

        Parameters
        ----------
        path : str
            The extension to send the PUT request to.
        data : any
            The data to include in the PUT request.
        content_type : Literal["application/json", "text/csv"], optional
            The content type of the data to be sent, by default "application/json"

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
        req_headers = self.auth_key.get_headers()

        if content_type == "application/json":
            response = self.session.put(path, headers=req_headers, json=data)
            response.raise_for_status()

        elif content_type == "text/csv":
            req_headers["Content-type"] = content_type
            response = self.session.put(path, headers=req_headers, data=data)
            response.raise_for_status()
        else:
            raise NotImplementedError(
                f"Put request with given content type '{content_type}' not implemented yet."
            )

        return response

    def get_projects(
        self,
        project_type: Type[T],
        name: Optional[str] = None,
        unit_id: Optional[str] = None,
        offset: int = 0,
    ) -> Result[T]:
        """Retrieve the available projects for the user

        Parameters
        ----------
        name : str, optional
            Filter projects by name, by default None
        unit_id : str, optional
            Filter projects by process unit ID, by default None
        offset : int, optional
            The offset for pagination, must be a non-negative integer, by default 0
        project_type : T, optional
            The type of project to retrieve, by default Project

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

        projects = project_type.requests(self)

        result = Result[project_type](
            offset=offset,
            limit=10,
            query_params=filter_params,
            requests=projects,
        )

        return result


class DataHowLabClient:
    """

    Client for the DHL API

    """

    def __init__(
        self,
        auth_key: APIKeyAuthentication,
        base_url: str,
        verify_ssl: Union[bool, str] = True,
    ):
        """
        Parameters
        ----------
        auth_key : APIKeyAuthentication
            An instance of the APIKeyAuthentication class containing the user's API key.
        base_url : str
            The URL address of the datahowlab application
        verify_ssl : Union[bool, str], optional
            Either a boolean, in which case it controls whether we verify the server's
            TLS certificate, or a string, in which case it must be a path to a CA bundle
            to use. For more info check the documentation for python's requests.request.
            By default True.

        Returns
        -------
        NoneType
            None
        """

        if isinstance(verify_ssl, bool) and not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self._client = Client(auth_key, base_url, verify=verify_ssl)

    def get_projects(
        self,
        name: Optional[str] = None,
        project_type: Literal["cultivation", "spectroscopy"] = "cultivation",
    ) -> Result[Project]:
        """
        Retrieves an iterable of Spectra projects from the DHL API.

        Parameters
        ----------
        name : str, optional
            A string to filter projects by name.
        offset : int, optional
            An integer representing the number of projects to skip before returning results.
        project_type : Literal["cultivation", "spectroscopy"], optional
            The type of project to retrieve, by default 'cultivation'

        Returns
        -------
        Result
            An Iterable object containing the retrieved projects
        """

        if project_type not in PROJECT_TYPE_MAP:
            raise ValueError(
                f"Type must be one of {list(PROJECT_TYPE_MAP.keys())}, but got '{project_type}'"
            )

        (unit_id, project_class) = PROJECT_TYPE_MAP[project_type]

        return self._client.get_projects(
            name=name,
            unit_id=unit_id,
            project_type=project_class,
        )

    def get_experiments(
        self, name: Optional[str] = None, product: Optional[Product] = None
    ) -> Result[Experiment]:
        """Retrieve the available experiments for the user

        Parameters
        ----------
        name : str, optional
            Search in DB by name, by default None
        product : Product, optional
            Filter experiments by product, by default None

        Returns
        -------
        Result
            An Iterable object containing the retrieved experiment data
        """

        product_id = product.id if product else None

        filter_params = {
            key: value
            for key, value in {
                "search": name,
                "filterBy[product._id]": product_id,
            }.items()
            if value is not None
        }

        experiments = Experiment.requests(self._client)
        result = Result[Experiment](
            offset=0,
            limit=10,
            query_params=filter_params,
            requests=experiments,
        )

        return result

    def get_products(self, code: Optional[str] = None) -> Result[Product]:
        """Retrieve the available products for the user

        Parameters
        ----------
        code : str, optional
            Filter products by code, by default None

        Returns
        -------
        Result
            An Iterable object containing the retrieved product data
        """

        filter_params = {"filterBy[code]": code} if code else None

        projects = Product.requests(self._client)
        result = Result[Product](
            offset=0,
            limit=10,
            query_params=filter_params,
            requests=projects,
        )

        return result

    def get_variables(
        self,
        code: Optional[str] = None,
        group: Optional[str] = None,
        variable_type: Optional[
            Literal["categorical", "flow", "logical", "numeric"]
        ] = None,
    ) -> Result[Variable]:
        """Retrieve the available variables for the user

        Parameters
        ----------
        code : str, optional
            Filter variables by code, by default None

        Returns
        -------
        Result
            An Iterable object containing the retrieved variable data
        """

        if variable_type and variable_type not in [
            "categorical",
            "flow",
            "logical",
            "numeric",
        ]:
            raise ValueError(
                (
                    f"Variable Type must be one of: 'categorical', 'flow',"
                    f" 'logical', 'numeric'. instead, it got '{variable_type}'"
                )
            )

        if group:
            variable_group_codes = VariableGroupCodes(
                self._client
            ).get_variable_group_codes()

            if group not in variable_group_codes:
                raise ValueError(
                    f"Variable Group must be one of: {list(variable_group_codes.keys())}."
                    f" instead, it got '{group}'"
                )

            group_id = variable_group_codes[group][0]
        else:
            group_id = None

        filter_params = {
            key: value
            for key, value in {
                "filterBy[code]": code,
                "filterBy[variant]": variable_type,
                "filterBy[group._id]": group_id,
            }.items()
            if value is not None
        }

        projects = Variable.requests(self._client)
        result = Result[Variable](
            offset=0,
            limit=10,
            query_params=filter_params,
            requests=projects,
        )

        return result

    def get_recipes(
        self, name: Optional[str] = None, product: Optional[Product] = None
    ) -> Result[Recipe]:
        """Retrieve the available recipes for the user

        Parameters
        ----------
        name : str, optional
            Filter recipes by name, by default None
        product : Product, optional
            Filter recipes by product, by default None

        Returns
        -------
        Result
            An Iterable object containing the retrieved recipe data
        """

        product_id = product.id if product else None

        filter_params = {
            key: value
            for key, value in {
                "filterBy[name]": name,
                "filterBy[product._id]": product_id,
            }.items()
            if value is not None
        }

        recipes = Recipe.requests(self._client)
        result = Result[Recipe](
            offset=0,
            limit=10,
            query_params=filter_params,
            requests=recipes,
        )

        return result

    def create(self, entity: DataBaseEntity) -> Optional[DataBaseEntity]:
        """Create a new entity in the database

        Parameters
        ----------
        entity : DataBaseEntity
            The entity to create in the database.
            This can be a Product, Variable, Recipe or Experiment.

        Returns
        -------
        DataBaseEntity
            The created entity
        """

        if entity.validate_import(self._client):
            return entity.requests(self._client).create(entity.create_request_body())
        else:
            return entity
