# Disable import cycle check: Client and some Entities have bidirectional references
# (those are only relevant for type checking)
# pyright: reportImportCycles=false
"""Client for the DHL API

This module defines the `DataHowLabClient` class,
which is used to interact with the DataHowLab's API.

Classes:
    - DataHowLabClient: main client to interact with the DHL API
"""

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from dhl_sdk._utils import paginate
from dhl_sdk.authentication import APIKeyAuthentication
from dhl_sdk import convert_tags_for_openapi

if TYPE_CHECKING:
    from openapi_client.models.process_format_code import ProcessFormatCode
    from openapi_client.models.process_unit_code import ProcessUnitCode
    from dhl_sdk.entities.experiment import Experiment
    from dhl_sdk.entities.product import Product
    from dhl_sdk.entities.project import Project
    from dhl_sdk.entities.variable import Variable
    from dhl_sdk.entities.variable_group import VariableGroup


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

        api_client = ApiClient(configuration=config)
        self.api = DefaultApi(api_client=api_client)

    def get_projects(
        self,
        search: str | None = None,
        name: str | None = None,
        tags: dict[str, str] | None = None,
        process_unit: "ProcessUnitCode | list[ProcessUnitCode] | None" = None,
        process_format: "ProcessFormatCode | list[ProcessFormatCode] | None" = None,
    ) -> "Iterator[Project]":
        """
        Retrieves an iterable of projects from the DHL API.

        Parameters
        ----------
        search : str, optional
            Free-text search to filter projects.
        name : str, optional
            Filter by project name (exact match).
        tags : dict[str, str], optional
            Filter by tags using key-value pairs (e.g., {"manufacturer": "example", "location": "plant1"}).
        process_unit : ProcessUnitCode | list[ProcessUnitCode], optional
            The process unit code(s) to filter by (e.g., ProcessUnitCode.BR for Bioreactor).
            Available values: BR (Bioreactor), SPC (Spectroscopy), IVT, PTC.
            Can be a single value or list. Defaults to all units if not specified.
        process_format : ProcessFormatCode | list[ProcessFormatCode], optional
            The process format code(s) to filter by (e.g., ProcessFormatCode.MAMMAL).
            Available values: MAMMAL, MICRO, MRNA.
            Can be a single value or list. Defaults to all formats if not specified.

        Returns
        -------
        Iterator
            An iterator of Project objects
        """
        from dhl_sdk.entities.project import Project

        process_unit_list: list[ProcessUnitCode] | None = None
        if isinstance(process_unit, list):
            process_unit_list = process_unit
        elif process_unit is not None:
            process_unit_list = [process_unit]

        process_format_list: list[ProcessFormatCode] | None = None
        if isinstance(process_format, list):
            process_format_list = process_format
        elif process_format is not None:
            process_format_list = [process_format]

        # Convert tags to OpenAPI format (dict[str, str] -> dict[str, dict[str, str]])
        tags_openapi = convert_tags_for_openapi(tags)

        for api_project in paginate(
            self.api.get_projects_api_v1_projects_get,
            search=search,
            name=name,
            tags=tags_openapi,
            process_unit=process_unit_list,
            process_format=process_format_list,
        ):
            yield Project(api_project, self.api)

    def get_experiments(
        self,
        search: str | None = None,
        tags: dict[str, str] | None = None,
        product_id: str | None = None,
        process_unit: "ProcessUnitCode | list[ProcessUnitCode] | None" = None,
        process_format: "ProcessFormatCode | list[ProcessFormatCode] | None" = None,
    ) -> "Iterator[Experiment]":
        """Retrieve the available experiments for the user

        Parameters
        ----------
        search : str, optional
            Free-text search to filter experiments.
        tags : dict[str, str], optional
            Filter by tags using key-value pairs (e.g., {"manufacturer": "example", "location": "plant1"}).
        product_id : str, optional
            Filter by experiment's product ID.
        process_unit : ProcessUnitCode | list[ProcessUnitCode], optional
            The process unit code(s) to filter by (e.g., ProcessUnitCode.BR for Bioreactor).
            Available values: BR (Bioreactor), SPC (Spectroscopy), IVT, PTC.
            Can be a single value or list. Defaults to all units if not specified.
        process_format : ProcessFormatCode | list[ProcessFormatCode], optional
            The process format code(s) to filter by (e.g., ProcessFormatCode.MAMMAL).
            Available values: MAMMAL, MICRO, MRNA.
            Can be a single value or list. Defaults to all formats if not specified.

        Returns
        -------
        Iterator
            An iterator of Experiment objects
        """
        from dhl_sdk.entities.experiment import Experiment

        process_unit_list: list[ProcessUnitCode] | None = None
        if isinstance(process_unit, list):
            process_unit_list = process_unit
        elif process_unit is not None:
            process_unit_list = [process_unit]

        process_format_list: list[ProcessFormatCode] | None = None
        if isinstance(process_format, list):
            process_format_list = process_format
        elif process_format is not None:
            process_format_list = [process_format]

        # Convert tags to OpenAPI format (dict[str, str] -> dict[str, dict[str, str]])
        tags_openapi = convert_tags_for_openapi(tags)

        for api_experiment in paginate(
            self.api.get_experiments_api_v1_experiments_get,
            search=search,
            tags=tags_openapi,
            product_id=product_id,
            process_unit=process_unit_list,
            process_format=process_format_list,
        ):
            yield Experiment(api_experiment, self.api)

    def get_products(
        self,
        search: str | None = None,
        name: str | None = None,
        code: str | None = None,
        tags: dict[str, str] | None = None,
        process_format: "ProcessFormatCode | list[ProcessFormatCode] | None" = None,
    ) -> "Iterator[Product]":
        """Retrieve the available products for the user

        Parameters
        ----------
        search : str, optional
            Free-text search to filter products.
        name : str, optional
            Filter by product name (exact match).
        code : str, optional
            Filter by product code (exact match).
        tags : dict[str, str], optional
            Filter by tags using key-value pairs (e.g., {"manufacturer": "example", "location": "plant1"}).
        process_format : ProcessFormatCode | list[ProcessFormatCode], optional
            The process format code(s) to filter by (e.g., ProcessFormatCode.MAMMAL).
            Available values: MAMMAL, MICRO, MRNA.
            Can be a single value or list. Defaults to all formats if not specified.

        Returns
        -------
        Iterator
            An iterator of Product objects
        """
        from dhl_sdk.entities.product import Product

        process_format_list: list[ProcessFormatCode] | None = None
        if isinstance(process_format, list):
            process_format_list = process_format
        elif process_format is not None:
            process_format_list = [process_format]

        # Convert tags to OpenAPI format (dict[str, str] -> dict[str, dict[str, str]])
        tags_openapi = convert_tags_for_openapi(tags)

        for api_product in paginate(
            self.api.get_products_api_v1_products_get,
            search=search,
            name=name,
            code=code,
            tags=tags_openapi,
            process_format=process_format_list,
        ):
            yield Product(api_product, self.api)

    def get_variables(
        self,
        search: str | None = None,
        name: str | None = None,
        code: str | None = None,
        tags: dict[str, str] | None = None,
        group_code: str | None = None,
        group_id: str | None = None,
        variant: str | None = None,
    ) -> "Iterator[Variable]":
        """Retrieve the available variables for the user

        Parameters
        ----------
        search : str, optional
            Free-text search to filter variables.
        name : str, optional
            Filter by variable name (exact match).
        code : str, optional
            Filter by variable code (exact match).
        tags : dict[str, str], optional
            Filter by tags using key-value pairs (e.g., {"manufacturer": "example", "location": "plant1"}).
        group_code : str, optional
            Filter by variable group code.
        group_id : str, optional
            Filter by variable group ID.
        variant : str, optional
            Filter by variable variant.

        Returns
        -------
        Iterator
            An iterator of Variable objects
        """
        from dhl_sdk.entities.variable import Variable

        # Convert tags to OpenAPI format (dict[str, str] -> dict[str, dict[str, str]])
        tags_openapi = convert_tags_for_openapi(tags)

        for api_variable in paginate(
            self.api.get_variables_api_v1_variables_get,
            search=search,
            name=name,
            code=code,
            tags=tags_openapi,
            group_code=group_code,
            group_id=group_id,
            variant=variant,
        ):
            yield Variable(api_variable)

    def get_variable_groups(
        self,
        process_unit: "ProcessUnitCode",
        process_format: "ProcessFormatCode",
        search: str | None = None,
        name: str | None = None,
        code: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> "Iterator[VariableGroup]":
        """Retrieve the available variable groups for the user

        Parameters
        ----------
        process_unit : ProcessUnitCode
            The process unit code to filter by (e.g., ProcessUnitCode.BR for Bioreactor).
            Available values: BR (Bioreactor), SPC (Spectroscopy), IVT, PTC.
            This parameter is required.
        process_format : ProcessFormatCode
            The process format code to filter by (e.g., ProcessFormatCode.MAMMAL).
            Available values: MAMMAL, MICRO, MRNA.
            This parameter is required.
        search : str, optional
            Free-text search to filter variable groups.
        name : str, optional
            Filter by variable group name (exact match).
        code : str, optional
            Filter by variable group code (exact match).
        tags : dict[str, str], optional
            Filter by tags using key-value pairs (e.g., {"manufacturer": "example", "location": "plant1"}).

        Returns
        -------
        Iterator
            An iterator of VariableGroup objects
        """
        from dhl_sdk.entities.variable_group import VariableGroup

        # Convert tags to OpenAPI format (dict[str, str] -> dict[str, dict[str, str]])
        tags_openapi = convert_tags_for_openapi(tags)

        for api_group in paginate(
            self.api.get_groups_api_v1_groups_get,
            search=search,
            name=name,
            code=code,
            tags=tags_openapi,
            process_unit=process_unit,
            process_format=process_format,
        ):
            yield VariableGroup(api_group)
