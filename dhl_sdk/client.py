"""Client for the DHL API

This module defines the `DataHowLabClient` class,
which is used to interact with the DataHowLab's API.

Classes:
    - DataHowLabClient: main client to interact with the DHL API
"""

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, TypeVar, final


from dhl_sdk.authentication import APIKeyAuthentication

if TYPE_CHECKING:
    from openapi_client.models.experiment import Experiment
    from openapi_client.models.process_format_code import ProcessFormatCode
    from openapi_client.models.process_unit_code import ProcessUnitCode
    from openapi_client.models.product import Product
    from openapi_client.models.project import Project
    from openapi_client.models.variable import Variable
    from openapi_client.models.variable_variant import VariableVariant

T = TypeVar("T")

try:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.api_client import ApiClient
    from openapi_client.configuration import Configuration
except ImportError:
    DefaultApi = None  # type: ignore[assignment, misc]
    ApiClient = None  # type: ignore[assignment, misc]
    Configuration = None  # type: ignore[assignment, misc]


@final
class DataHowLabClient:
    """
    Client for the DHL API
    """

    def __init__(
        self,
        auth_key: APIKeyAuthentication,
        base_url: str,
        verify_ssl: bool | str = True,
    ):
        """
        Parameters
        ----------
        auth_key : APIKeyAuthentication
            An instance of the APIKeyAuthentication class containing the user's API key.
        base_url : str
            The URL address of the datahowlab application
        verify_ssl : bool | str, optional
            Either a boolean, in which case it controls whether we verify the server's
            TLS certificate, or a string, in which case it must be a path to a CA bundle
            to use. For more info check the documentation for python's requests.request.
            By default True.

        Returns
        -------
        NoneType
            None
        """
        if DefaultApi is None or ApiClient is None or Configuration is None:
            raise ImportError("OpenAPI client not available. Please regenerate the API client using openapi-generator-cli.")

        config = Configuration(host=base_url.rstrip("/"))
        config.verify_ssl = bool(verify_ssl)
        config.api_key = {"APIKeyHeader": auth_key.api_key}
        config.api_key_prefix = {"APIKeyHeader": "ApiKey"}

        api_client = ApiClient(configuration=config)
        self._api = DefaultApi(api_client=api_client)

    def _paginate(self, getter_func: Callable[..., list[T]], **kwargs: Any) -> Iterator[T]:  # pyright: ignore[reportAny, reportExplicitAny]
        """Internal method to handle pagination"""
        skip = 0
        limit = 10

        while True:
            items = getter_func(skip=skip, limit=limit, **kwargs)

            if not items:
                break

            for item in items:
                yield item

            if len(items) < limit:
                break

            skip += limit

    def get_projects(
        self,
        name: str | None = None,
        process_unit: "ProcessUnitCode | list[ProcessUnitCode] | None" = None,
        process_format: "ProcessFormatCode | list[ProcessFormatCode] | None" = None,
    ) -> "Iterator[Project]":
        """
        Retrieves an iterable of projects from the DHL API.

        Parameters
        ----------
        name : str, optional
            A string to filter projects by name (free-text search).
        process_unit : ProcessUnitCode | List[ProcessUnitCode], optional
            The process unit code(s) to filter by (e.g., ProcessUnitCode.BR for Bioreactor).
            Available values: BR (Bioreactor), SPC (Spectroscopy), IVT, PTC.
            Can be a single value or list. Defaults to all units if not specified.
        process_format : ProcessFormatCode | List[ProcessFormatCode], optional
            The process format code(s) to filter by (e.g., ProcessFormatCode.MAMMAL).
            Available values: MAMMAL, MICRO, MRNA.
            Can be a single value or list. Defaults to all formats if not specified.

        Returns
        -------
        Iterator
            An iterator of Project objects
        """
        process_unit_list = [process_unit] if process_unit and not isinstance(process_unit, list) else process_unit
        process_format_list = [process_format] if process_format and not isinstance(process_format, list) else process_format

        return self._paginate(
            self._api.get_projects_api_v1_projects_get,
            search=name,
            process_unit=process_unit_list,
            process_format=process_format_list,
        )

    def get_experiments(
        self,
        name: str | None = None,
        process_unit: "ProcessUnitCode | list[ProcessUnitCode] | None" = None,
        process_format: "ProcessFormatCode | list[ProcessFormatCode] | None" = None,
    ) -> "Iterator[Experiment]":
        """Retrieve the available experiments for the user

        Parameters
        ----------
        name : str, optional
            Search in DB by name (free-text search), by default None
        process_unit : ProcessUnitCode | List[ProcessUnitCode], optional
            The process unit code(s) to filter by (e.g., ProcessUnitCode.BR for Bioreactor).
            Available values: BR (Bioreactor), SPC (Spectroscopy), IVT, PTC.
            Can be a single value or list. Defaults to all units if not specified.
        process_format : ProcessFormatCode | List[ProcessFormatCode], optional
            The process format code(s) to filter by (e.g., ProcessFormatCode.MAMMAL).
            Available values: MAMMAL, MICRO, MRNA.
            Can be a single value or list. Defaults to all formats if not specified.

        Returns
        -------
        Iterator
            An iterator of Experiment objects
        """
        process_unit_list = [process_unit] if process_unit and not isinstance(process_unit, list) else process_unit
        process_format_list = [process_format] if process_format and not isinstance(process_format, list) else process_format

        return self._paginate(
            self._api.get_experiments_api_v1_experiments_get,
            search=name,
            process_unit=process_unit_list,
            process_format=process_format_list,
        )

    def get_products(
        self,
        code: str | None = None,
        name: str | None = None,
        process_format: "ProcessFormatCode | list[ProcessFormatCode] | None" = None,  # type: ignore[name-defined]
    ) -> "Iterator[Product]":
        """Retrieve the available products for the user

        Parameters
        ----------
        code : str, optional
            Filter products by code, by default None
        name : str, optional
            Search products by name (free-text search), by default None
        process_format : ProcessFormatCode | List[ProcessFormatCode], optional
            The process format code(s) to filter by (e.g., ProcessFormatCode.MAMMAL).
            Available values: MAMMAL, MICRO, MRNA.
            Can be a single value or list. Defaults to all formats if not specified.

        Returns
        -------
        Iterator
            An iterator of Product objects
        """
        process_format_list = [process_format] if process_format and not isinstance(process_format, list) else process_format

        return self._paginate(
            self._api.get_products_api_v1_products_get,
            code=code,
            search=name,
            process_format=process_format_list,
        )

    def get_variables(
        self,
        code: str | None = None,
        name: str | None = None,
        variant: "VariableVariant | list[VariableVariant] | None" = None,  # type: ignore[name-defined]
    ) -> "Iterator[Variable]":
        """Retrieve the available variables for the user

        Parameters
        ----------
        code : str, optional
            Filter variables by code, by default None
        name : str, optional
            Search variables by name (free-text search), by default None
        variant : VariableVariant | List[VariableVariant], optional
            Filter by variable variant type(s) (e.g., VariableVariant.NUMERIC).
            Available values: FLOW, NUMERIC, CATEGORICAL, LOGICAL, SPECTRUM.
            Can be a single value or list. Defaults to all variants if not specified.

        Returns
        -------
        Iterator
            An iterator of Variable objects
        """
        variant_list = [variant] if variant and not isinstance(variant, list) else variant

        return self._paginate(
            self._api.get_variables_api_v1_variables_get,
            code=code,
            search=name,
            variant=variant_list,
        )
