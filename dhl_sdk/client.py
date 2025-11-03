"""Simplified DataHowLab Client for SDK v2

This module provides the main client class for interacting with the DataHowLab API.
All operations go through this single client class with intuitive method names.
"""

import os
from typing import Any, Literal
from urllib.parse import urlencode
from urllib.parse import urljoin as urllib_urljoin

import requests
import urllib3
from pydantic import ValidationError as PydanticValidationError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from dhl_sdk._constants import (
    DATASETS_URL,
    EXPERIMENTS_URL,
    FILES_URL,
    GROUPS_URL,
    MODELS_URL,
    PREDICT_URL,
    PROCESS_FORMAT_MAP,
    PROCESS_UNIT_MAP,
    PRODUCTS_URL,
    PROJECTS_URL,
    RECIPES_URL,
    VARIABLES_URL,
)
from dhl_sdk.errors import (
    APIError,
    AuthenticationError,
    DHLError,
    EntityNotFoundError,
    PermissionDeniedError,
    PredictionError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from dhl_sdk.models import (
    Dataset,
    Experiment,
    Model,
    Product,
    Project,
    Recipe,
    Variable,
)
from dhl_sdk.pagination import PageIterator
from dhl_sdk.services import DataFormatService, FileService
from dhl_sdk.types import (
    CategoricalVariable,
    ExperimentData,
    FlowReference,
    FlowVariable,
    HistoricalPredictionInput,
    LogicalVariable,
    NumericVariable,
    PredictionOutput,
    PropagationPredictionInput,
    SpectraExperimentData,
    SpectraPredictionInput,
    SpectrumAxis,
    SpectrumVariable,
    TimeseriesData,
    VariableType,
)


class DataHowLabClient:
    """Main client for interacting with the DataHow Lab API

    This client provides a simple, type-safe interface for all DataHowLab operations.

    Examples:
        >>> client = DataHowLabClient(api_key="your-key", base_url="https://...")
        >>> product = client.create_product(code="PROD", name="My Product")
        >>> products = client.list_products(code="PROD")
        >>> experiments = client.list_experiments(product=product)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "",
        verify_ssl: bool | str = True,
        timeout: float = 30.0,
        file_service: FileService | None = None,
        data_format_service: DataFormatService | None = None,
    ):
        """Initialize the DataHowLab client

        Args:
            api_key: API key for authentication. If None, reads from DHL_API_KEY env var
            base_url: Base URL of the DataHowLab instance (e.g., "https://yourdomain.datahowlab.ch/")
            verify_ssl: SSL verification. Can be True (verify), False (no verify), or path to CA bundle
            timeout: Request timeout in seconds (default: 30.0). Set to None to disable timeout.
            file_service: Optional FileService instance for dependency injection (mainly for testing)
            data_format_service: Optional DataFormatService instance for dependency injection (mainly for testing)

        Raises:
            AuthenticationError: If API key is not provided and not in environment

        Examples:
            >>> # Production usage (services auto-created)
            >>> client = DataHowLabClient(api_key="key", base_url="https://...")
            >>>
            >>> # Testing usage (inject mocks)
            >>> mock_file_service = Mock(spec=FileService)
            >>> client = DataHowLabClient(
            ...     api_key="key",
            ...     base_url="https://...",
            ...     file_service=mock_file_service
            ... )
        """
        # Get API key
        self.api_key = api_key or os.environ.get("DHL_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key not provided. Pass api_key or set DHL_API_KEY environment variable"
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Disable SSL warnings if verification is disabled
        if isinstance(verify_ssl, bool) and not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Create session with retry strategy
        self.session = self._create_session(verify_ssl)

        # Cache for variable groups
        self._variable_groups_cache: dict[str, tuple[str, str]] | None = None

        # Initialize services (allow injection for testing)
        self.file_service = file_service or FileService(
            request_func=self._request, files_url=FILES_URL
        )
        self.data_format = data_format_service or DataFormatService()

    def _create_session(self, verify: bool | str) -> requests.Session:
        """Create requests session with retry strategy"""
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.verify = verify
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _get_headers(self) -> dict[str, str]:
        """Get authorization headers for API requests"""
        return {"Authorization": f"ApiKey {self.api_key}"}

    def _make_url(self, path: str) -> str:
        """Construct full URL from path"""
        return urllib_urljoin(self.base_url, path)

    def _sanitize_response_body(
        self, body: str | None, max_length: int = 500
    ) -> str | None:
        """Sanitize response body to prevent credential leakage in errors

        Args:
            body: Raw response body text
            max_length: Maximum length before truncation (default: 500)

        Returns:
            Sanitized response body with sensitive data redacted

        Examples:
            >>> body = '{"api_key": "secret123", "data": "..."}'
            >>> client._sanitize_response_body(body)
            '{"api_key": "***REDACTED***", "data": "..."}'
        """
        if not body:
            return None

        import re

        # Truncate long responses to prevent log spam
        if len(body) > max_length:
            body = body[:max_length] + "... (truncated)"

        # Redact potential sensitive patterns
        # Pattern 1: API keys in JSON (api_key, apiKey, API_KEY, etc.)
        body = re.sub(
            r'(["\'](?:api[_-]?key|token|password|secret)["\']?\s*:\s*["\'])[^"\']+',
            r"\1***REDACTED***",
            body,
            flags=re.IGNORECASE,
        )

        # Pattern 2: Authorization headers
        body = re.sub(
            r"(Authorization:\s*(?:Bearer|ApiKey|Basic)\s+)[^\s]+",
            r"\1***REDACTED***",
            body,
            flags=re.IGNORECASE,
        )

        return body

    def _request(
        self,
        method: str,
        path: str,
        json_data: Any | None = None,
        query_params: dict[str, str] | None = None,
        data: Any | None = None,
        content_type: str | None = None,
    ) -> requests.Response:
        """Make HTTP request to API

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            path: API path
            json_data: JSON data for request body
            query_params: Query parameters
            data: Raw data for request body
            content_type: Content type for raw data

        Returns:
            Response object

        Raises:
            APIError: If request fails
            AuthenticationError: If authentication fails (401)
        """
        # Build URL with query params
        url = path
        if query_params:
            query_string = urlencode(query_params, doseq=True, safe="[]")
            url = f"{path}?{query_string}"

        url = self._make_url(url)

        # Prepare headers
        headers = self._get_headers()
        if content_type:
            headers["Content-Type"] = content_type

        # Make request
        try:
            if json_data is not None:
                response = self.session.request(
                    method, url, headers=headers, json=json_data, timeout=self.timeout
                )
            elif data is not None:
                response = self.session.request(
                    method, url, headers=headers, data=data, timeout=self.timeout
                )
            else:
                response = self.session.request(
                    method, url, headers=headers, timeout=self.timeout
                )

            # Handle specific HTTP status codes with appropriate exceptions
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or unauthorized access")
            elif response.status_code == 403:
                raise PermissionDeniedError(
                    "Access forbidden. Check your permissions for this resource."
                )
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                retry_seconds = int(retry_after) if retry_after else None
                raise RateLimitError(
                    "Rate limit exceeded. Please wait before retrying.",
                    retry_after=retry_seconds,
                )
            elif response.status_code in (500, 502, 503, 504):
                raise ServerError(
                    f"Server error ({response.status_code}). "
                    "The API is experiencing issues. Please try again later.",
                    status_code=response.status_code,
                )

            # For other errors, let requests handle it
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            raise APIError(
                f"Request timed out after {self.timeout} seconds. "
                "Try increasing the timeout parameter or check your network connection.",
                status_code=None,
                response_body=None,
            ) from e
        except requests.exceptions.HTTPError as e:
            # Re-raise our custom exceptions if they were raised above
            if isinstance(e.__cause__, DHLError):
                raise e.__cause__ from e
            # Otherwise, wrap in generic APIError with sanitized response
            sanitized_body = (
                self._sanitize_response_body(e.response.text) if e.response else None
            )
            raise APIError(
                f"API request failed: {e}",
                status_code=e.response.status_code if e.response else None,
                response_body=sanitized_body,
            ) from e
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}") from e

    # ========================================================================
    # Product Operations
    # ========================================================================

    def create_product(
        self,
        code: str,
        name: str,
        description: str = "",
        process_format: Literal["mammalian", "microbial"] = "mammalian",
    ) -> Product:
        """Create a new product

        Args:
            code: Product code (1-10 characters, unique)
            name: Product name
            description: Optional description
            process_format: Process format type

        Returns:
            Created Product with ID

        Raises:
            ValidationError: If input validation fails
            EntityAlreadyExistsError: If product with code already exists
            APIError: If API request fails
        """
        # Validate with Pydantic
        try:
            product = Product(
                code=code,
                name=name,
                description=description,
                process_format=process_format,
            )
        except PydanticValidationError as e:
            # Convert Pydantic validation error to our custom error
            first_error = e.errors()[0]
            raise ValidationError(
                message=first_error["msg"],
                field=str(first_error["loc"][0]) if first_error["loc"] else "unknown",
                value=first_error.get("input"),
            ) from e

        # Prepare request body
        body = {
            "code": product.code,
            "name": product.name,
            "description": product.description,
            "processFormatId": PROCESS_FORMAT_MAP[product.process_format],
        }

        # Create product
        response = self._request("POST", PRODUCTS_URL, json_data=body)
        data = response.json()

        return Product(
            id=data["id"],
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
            process_format=process_format,
        )

    def _list_products_page(
        self, code: str | None, offset: int, limit: int
    ) -> list[Product]:
        """Internal: Fetch a single page of products"""
        query_params: dict[str, str] = {
            "limit": str(limit),
            "offset": str(offset),
            "archived": "false",
            "sortBy[createdAt]": "desc",
        }

        if code:
            query_params["filterBy[code]"] = code

        response = self._request("GET", PRODUCTS_URL, query_params=query_params)
        data = response.json()

        products = []
        for item in data:
            # Resolve process format from ID
            process_format_id = item.get("processFormatId")
            process_format = next(
                (k for k, v in PROCESS_FORMAT_MAP.items() if v == process_format_id),
                "mammalian",
            )

            products.append(
                Product(
                    id=item["id"],
                    code=item["code"],
                    name=item["name"],
                    description=item.get("description", ""),
                    process_format=process_format,
                )
            )

        return products

    def list_products(
        self,
        code: str | None = None,
        limit: int = 100,
        iter_all: bool = False,
    ) -> list[Product] | PageIterator[Product]:
        """List products

        Args:
            code: Optional code filter
            limit: Maximum number of results per page (default 100)
            iter_all: If True, returns an iterator that fetches all results across pages.
                     If False (default), returns only the first page as a list.

        Returns:
            List of Product objects (first page only) or PageIterator for all results

        Examples:
            >>> # Get first 100 products
            >>> products = client.list_products()
            >>>
            >>> # Iterate over ALL products (fetches pages as needed)
            >>> for product in client.list_products(iter_all=True):
            ...     print(product.code)
        """
        # Fetch first page
        first_page = self._list_products_page(code, offset=0, limit=limit)

        # Return iterator if requested
        if iter_all:
            # Create iterator that continues from second page
            iterator = PageIterator(
                fetch_page=lambda offset, page_limit: self._list_products_page(
                    code, offset, page_limit
                ),
                page_size=limit,
                initial_offset=len(first_page),  # Start from where first page ended
            )
            # Pre-populate with first page
            iterator.current_page = first_page
            iterator.current_index = 0
            if len(first_page) < limit:
                iterator.exhausted = True
            return iterator

        return first_page

    def get_product(self, product_id: str) -> Product:
        """Get a product by ID

        Args:
            product_id: Product ID

        Returns:
            Product object

        Raises:
            EntityNotFoundError: If product not found
        """
        try:
            response = self._request("GET", f"{PRODUCTS_URL}/{product_id}")
            item = response.json()

            process_format_id = item.get("processFormatId")
            process_format = next(
                (k for k, v in PROCESS_FORMAT_MAP.items() if v == process_format_id),
                "mammalian",
            )

            return Product(
                id=item["id"],
                code=item["code"],
                name=item["name"],
                description=item.get("description", ""),
                process_format=process_format,
            )
        except APIError as e:
            if e.status_code == 404:
                raise EntityNotFoundError("Product not found", entity_type="Product", entity_id=product_id) from e
            raise

    # ========================================================================
    # Variable Operations
    # ========================================================================

    def _get_variable_groups(self) -> dict[str, tuple[str, str]]:
        """Get variable groups from API (cached)

        Returns:
            Dict mapping group name to (group_id, group_code)
        """
        if self._variable_groups_cache is not None:
            return self._variable_groups_cache

        response = self._request("GET", GROUPS_URL)
        groups = response.json()

        self._variable_groups_cache = {
            group["name"]: (group["id"], group["code"]) for group in groups
        }

        return self._variable_groups_cache

    def create_variable(
        self,
        code: str,
        name: str,
        unit: str,
        group: str,
        type: VariableType,
        description: str = "",
    ) -> Variable:
        """Create a new variable

        Args:
            code: Variable code (unique)
            name: Variable name
            unit: Measurement unit
            group: Variable group name (e.g., "X Variables", "Z Variables")
            type: Variable type (NumericVariable, CategoricalVariable, etc.)
            description: Optional description

        Returns:
            Created Variable with ID

        Raises:
            ValidationError: If input validation fails or group doesn't exist
            EntityAlreadyExistsError: If variable with code already exists
        """
        # Validate with Pydantic
        variable = Variable(
            code=code,
            name=name,
            unit=unit,
            group=group,
            type=type,
            description=description,
        )

        # Resolve group name to ID
        groups = self._get_variable_groups()
        if variable.group not in groups:
            valid_groups = list(groups.keys())
            raise ValidationError(
                f"Invalid variable group. Valid groups: {valid_groups}",
                field="group",
                value=variable.group,
            )

        group_id, _ = groups[variable.group]

        # Prepare request body
        body = {
            "code": variable.code,
            "name": variable.name,
            "measurementUnit": variable.unit,
            "description": variable.description,
            "group": {"id": group_id},
            "variant": variable.type.kind,
            variable.type.kind: variable.type.model_dump(
                by_alias=True, exclude={"kind"}, exclude_none=True
            ),
        }

        # Create variable
        response = self._request("POST", VARIABLES_URL, json_data=body)
        data = response.json()

        return Variable(
            id=data["id"],
            code=data["code"],
            name=data["name"],
            unit=data["measurementUnit"],
            group=variable.group,
            type=type,
            description=data.get("description", ""),
        )

    def _parse_numeric_variable(self, data: dict) -> NumericVariable:
        """Parse numeric variable type from API response"""
        return NumericVariable(
            min=data.get("min"),
            max=data.get("max"),
            default=data.get("default"),
            interpolation=data.get("interpolation"),
        )

    def _parse_categorical_variable(self, data: dict) -> CategoricalVariable:
        """Parse categorical variable type from API response"""
        return CategoricalVariable(
            categories=data.get("categories") or [],
            strict=data.get("strict", False),
            default=data.get("default"),
        )

    def _parse_logical_variable(self, data: dict) -> LogicalVariable:
        """Parse logical variable type from API response"""
        return LogicalVariable(default=data.get("default"))

    def _parse_flow_variable(self, data: dict) -> FlowVariable:
        """Parse flow variable type from API response"""
        references = []
        for ref_data in data.get("references", []):
            references.append(
                FlowReference(
                    measurement=ref_data.get("measurementId", ""),
                    concentration=ref_data.get("concentrationId"),
                    fraction=ref_data.get("fractionId"),
                )
            )

        return FlowVariable(
            flow_type=data.get("flowType", "bolus"),
            references=references,
            step_size=data.get("stepSize"),
            volume_variable=data.get("volumeId"),
        )

    def _parse_spectrum_variable(self, data: dict) -> SpectrumVariable:
        """Parse spectrum variable type from API response"""
        x_axis_data = data.get("xAxis", {})
        y_axis_data = data.get("yAxis", {})

        return SpectrumVariable(
            x_axis=SpectrumAxis(
                dimension=x_axis_data.get("dimension"),
                unit=x_axis_data.get("unit"),
                min=x_axis_data.get("min"),
                max=x_axis_data.get("max"),
                label=x_axis_data.get("label"),
            )
            if x_axis_data
            else None,
            y_axis=SpectrumAxis(label=y_axis_data.get("label"))
            if y_axis_data
            else None,
        )

    def _parse_variable_type(self, variant: str, variant_data: dict) -> VariableType:
        """Parse variable type from API response based on variant

        Args:
            variant: Variable variant/type name
            variant_data: Type-specific data from API

        Returns:
            Appropriate VariableType subclass instance

        Raises:
            ValidationError: If variant type is unknown
        """
        parsers = {
            "numeric": self._parse_numeric_variable,
            "categorical": self._parse_categorical_variable,
            "logical": self._parse_logical_variable,
            "flow": self._parse_flow_variable,
            "spectrum": self._parse_spectrum_variable,
        }

        parser = parsers.get(variant)
        if not parser:
            raise ValidationError(
                f"Unknown variable variant: {variant}",
                field="variant",
                value=variant,
            )

        return parser(variant_data)

    def _parse_variable(self, item: dict) -> Variable:
        """Parse Variable object from API response item

        Args:
            item: Variable data from API response

        Returns:
            Variable object with parsed type
        """
        variant = item.get("variant")
        variant_data = item.get(variant, {})

        var_type = self._parse_variable_type(variant, variant_data)

        return Variable(
            id=item["id"],
            code=item["code"],
            name=item["name"],
            unit=item.get("measurementUnit", ""),
            group=item.get("group", {}).get("name", ""),
            type=var_type,
            description=item.get("description", ""),
        )

    def list_variables(
        self,
        code: str | None = None,
        group: str | None = None,
        variable_type: Literal["numeric", "categorical", "logical", "flow", "spectrum"]
        | None = None,
        limit: int = 100,
    ) -> list[Variable]:
        """List variables

        Args:
            code: Optional code filter
            group: Optional group name filter
            variable_type: Optional type filter
            limit: Maximum number of results

        Returns:
            List of Variable objects
        """
        query_params: dict[str, str] = {
            "limit": str(limit),
            "offset": "0",
            "archived": "false",
            "sortBy[createdAt]": "desc",
        }

        if code:
            query_params["filterBy[code]"] = code

        if variable_type:
            query_params["filterBy[variant]"] = variable_type

        if group:
            groups = self._get_variable_groups()
            if group in groups:
                group_id, _ = groups[group]
                query_params["filterBy[group._id]"] = group_id

        response = self._request("GET", VARIABLES_URL, query_params=query_params)
        data = response.json()

        return [self._parse_variable(item) for item in data]

    # ========================================================================
    # Experiment Operations
    # ========================================================================

    def create_experiment(
        self,
        name: str,
        product: Product | str,
        variables: list[Variable | str],
        data: ExperimentData | SpectraExperimentData,
        description: str = "",
        process_format: Literal["mammalian", "microbial"] = "mammalian",
    ) -> Experiment:
        """Create a new experiment

        Args:
            name: Experiment name
            product: Product object or product ID
            variables: List of Variable objects or variable IDs
            data: Experiment data (ExperimentData or SpectraExperimentData)
            description: Optional description
            process_format: Process format

        Returns:
            Created Experiment with ID

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        # Validate experiment object
        experiment = Experiment(
            name=name,
            description=description,
            product=product,
            process_format=process_format,
            variant=data.variant,
            variables=variables,
        )

        # Resolve product ID
        product_id = product.id if isinstance(product, Product) else product

        # Resolve variable IDs
        variable_ids = [(v.id if isinstance(v, Variable) else v) for v in variables]

        # Upload data files and get file IDs/instances
        instances = self._create_experiment_files(variables, data)

        # Prepare request body
        body = {
            "name": experiment.name,
            "description": experiment.description,
            "product": {"id": product_id},
            "processFormatId": PROCESS_FORMAT_MAP[experiment.process_format],
            "processUnitId": PROCESS_UNIT_MAP["cultivation"],  # Default to cultivation
            "variables": [{"id": vid} for vid in variable_ids],
            "instances": instances,
            "variant": experiment.variant,
        }

        # Add variant-specific fields
        if experiment.variant == "run" and isinstance(data, ExperimentData):
            body["run"] = {
                "startTime": data.start_time.isoformat() if data.start_time else None,
                "endTime": data.end_time.isoformat() if data.end_time else None,
            }

        # Create experiment
        response = self._request("POST", EXPERIMENTS_URL, json_data=body)
        response_data = response.json()

        return Experiment(
            id=response_data["id"],
            name=response_data["name"],
            description=response_data.get("description", ""),
            product=product,
            process_format=experiment.process_format,
            variant=experiment.variant,
            variables=variables,
        )

    def _create_experiment_files(
        self,
        variables: list[Variable | str],
        data: ExperimentData | SpectraExperimentData,
    ) -> list[dict]:
        """Internal: Create file uploads for experiment data

        Returns:
            List of instances (column/fileId mappings)
        """
        instances = []

        if isinstance(data, SpectraExperimentData):
            # Handle spectra experiment
            # 1. Upload spectra file
            spectra_csv = self._format_spectra_csv(data.spectra)
            spectra_file_id = self._upload_file(
                name="spectra_data",
                file_type="runSpectra" if data.variant == "run" else "sampleSpectra",
                data=spectra_csv,
                content_type="text/csv",
            )
            instances.append({"column": "1", "fileId": spectra_file_id})

            # 2. Upload other variables file
            if data.inputs:
                vars_data = {
                    "timeseries": {
                        code: {"timestamps": [], "values": values}
                        for code, values in data.inputs.items()
                    }
                }
                vars_file_id = self._upload_file(
                    name="variables_data",
                    file_type="runData" if data.variant == "run" else "sampleData",
                    data=vars_data,
                    content_type="application/json",
                )
                # Add instance for each non-spectra variable
                for var in variables:
                    var_code = var.code if isinstance(var, Variable) else var
                    if var_code in data.inputs:
                        instances.append({"column": var_code, "fileId": vars_file_id})

        else:
            # Handle regular experiment - use DataFormatService
            timeseries_data = self.data_format.format_timeseries_to_json(
                data.timeseries
            )
            file_id = self._upload_file(
                name="experiment_data",
                file_type="runData" if data.variant == "run" else "sampleData",
                data=timeseries_data,
                content_type="application/json",
            )
            # Add instance for each variable
            for code in data.timeseries:
                instances.append({"column": code, "fileId": file_id})

        return instances

    def _format_spectra_csv(self, spectra: Any) -> str:
        """Format spectra data as CSV string (delegated to DataFormatService)"""
        return self.data_format.format_spectra_to_csv(spectra)

    def _upload_file(
        self,
        name: str,
        file_type: str,
        data: dict | str,
        content_type: str,
    ) -> str:
        """Internal: Upload file data and return file ID (delegated to FileService)"""
        return self.file_service.upload_file(name, file_type, data, content_type)

    def list_experiments(
        self,
        name: str | None = None,
        product: Product | str | None = None,
        limit: int = 100,
    ) -> list[Experiment]:
        """List experiments

        Args:
            name: Optional name search filter
            product: Optional product filter (Product object or ID)
            limit: Maximum number of results

        Returns:
            List of Experiment objects
        """
        query_params: dict[str, str] = {
            "limit": str(limit),
            "offset": "0",
            "archived": "false",
            "sortBy[createdAt]": "desc",
        }

        if name:
            query_params["search"] = name

        if product:
            product_id = product.id if isinstance(product, Product) else product
            query_params["filterBy[product._id]"] = product_id

        response = self._request("GET", EXPERIMENTS_URL, query_params=query_params)
        data = response.json()

        experiments = []
        for item in data:
            experiments.append(
                Experiment(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    product=item.get("product", {}).get("id", ""),
                    process_format="mammalian",  # Simplified
                    variant=item.get("variant", "run"),
                    variables=[],  # Simplified
                )
            )

        return experiments

    def get_experiment(self, experiment_id: str) -> Experiment:
        """Get experiment by ID"""
        try:
            response = self._request("GET", f"{EXPERIMENTS_URL}/{experiment_id}")
            item = response.json()

            return Experiment(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                product=item.get("product", {}).get("id", ""),
                process_format="mammalian",
                variant=item.get("variant", "run"),
                variables=[],
            )
        except APIError as e:
            if e.status_code == 404:
                raise EntityNotFoundError("Experiment not found", entity_type="Experiment", entity_id=experiment_id) from e
            raise

    def get_experiment_data(self, experiment: Experiment | str) -> dict[str, dict]:
        """Get data for an experiment

        Args:
            experiment: Experiment object or experiment ID

        Returns:
            Dict mapping variable code to {timestamps: [...], values: [...]}

        Raises:
            EntityNotFoundError: If experiment not found
            APIError: If data retrieval fails
        """
        exp_id = experiment.id if isinstance(experiment, Experiment) else experiment

        # Fetch full experiment with instances
        response = self._request("GET", f"{EXPERIMENTS_URL}/{exp_id}")
        exp_data = response.json()

        instances = exp_data.get("instances", [])
        if not instances:
            return {}

        # Cache for downloaded files (avoid downloading same file multiple times)
        file_cache: dict[str, requests.Response] = {}
        experiment_data: dict[str, dict] = {}

        for instance in instances:
            file_id = instance.get("fileId")
            column = instance.get("column")

            if not file_id or not column:
                continue

            # Skip if we've already processed this column
            if column in experiment_data:
                continue

            # Download file if not cached
            if file_id not in file_cache:
                file_response = self.file_service.download_file(file_id)
                file_cache[file_id] = file_response
            else:
                file_response = file_cache[file_id]

            # Parse based on content type
            content_type = file_response.headers.get("content-type", "")

            if "application/json" in content_type:
                # Time-series data
                data = file_response.json()
                timeseries = data.get("timeseries", {})
                if column in timeseries:
                    experiment_data[column] = timeseries[column]

            elif "text/csv" in content_type:
                # Spectra data - delegate parsing to DataFormatService
                spectra_data = self.data_format.parse_csv_to_spectra(
                    file_response.text, exp_data.get("variant", "run")
                )
                if spectra_data:
                    experiment_data["spectra"] = spectra_data

        return experiment_data

    # ========================================================================
    # Recipe Operations
    # ========================================================================

    def create_recipe(
        self,
        name: str,
        product: Product | str,
        variables: list[Variable | str],
        data: dict[str, TimeseriesData],
        description: str = "",
        duration: int | None = None,
    ) -> Recipe:
        """Create a new recipe

        Args:
            name: Recipe name
            product: Product object or product ID
            variables: List of Variable objects or variable IDs
            data: Dictionary mapping variable code to TimeseriesData
            description: Optional description
            duration: Optional duration in seconds

        Returns:
            Created Recipe with ID

        Raises:
            ValidationError: If input validation fails
            APIError: If API request fails
        """
        # Validate recipe object
        recipe = Recipe(
            name=name,
            description=description,
            product=product,
            duration=duration,
            variables=variables,
        )

        # Resolve product ID
        product_id = product.id if isinstance(product, Product) else product

        # Resolve variable IDs
        variable_ids = [(v.id if isinstance(v, Variable) else v) for v in variables]

        # Upload recipe data file - use DataFormatService
        timeseries_data = self.data_format.format_timeseries_to_json(data)

        file_id = self._upload_file(
            name=f"recipe_{name}_data",
            file_type="runData",
            data=timeseries_data,
            content_type="application/json",
        )

        # Create instances (map variable codes to file columns)
        instances = [{"column": code, "fileId": file_id} for code in data]

        # Prepare request body
        body = {
            "name": recipe.name,
            "description": recipe.description,
            "product": {"id": product_id},
            "variables": [{"id": vid} for vid in variable_ids],
            "instances": instances,
        }

        if duration is not None:
            body["duration"] = duration

        # Create recipe
        response = self._request("POST", RECIPES_URL, json_data=body)
        response_data = response.json()

        return Recipe(
            id=response_data["id"],
            name=response_data["name"],
            description=response_data.get("description", ""),
            product=product,
            duration=response_data.get("duration"),
            variables=variables,
        )

    def list_recipes(
        self,
        name: str | None = None,
        product: Product | str | None = None,
        limit: int = 100,
    ) -> list[Recipe]:
        """List recipes

        Args:
            name: Optional name filter
            product: Optional product filter (Product object or ID)
            limit: Maximum number of results

        Returns:
            List of Recipe objects
        """
        query_params: dict[str, str] = {
            "limit": str(limit),
            "offset": "0",
            "archived": "false",
            "sortBy[createdAt]": "desc",
        }

        if name:
            query_params["filterBy[name]"] = name

        if product:
            product_id = product.id if isinstance(product, Product) else product
            query_params["filterBy[product._id]"] = product_id

        response = self._request("GET", RECIPES_URL, query_params=query_params)
        data = response.json()

        recipes = []
        for item in data:
            recipes.append(
                Recipe(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    product=item.get("product", {}).get("id", ""),
                    duration=item.get("duration"),
                    variables=[],  # Simplified
                )
            )

        return recipes

    # ========================================================================
    # Project Operations
    # ========================================================================

    def list_projects(
        self,
        name: str | None = None,
        project_type: Literal["cultivation", "spectroscopy"] = "cultivation",
        process_format: Literal["mammalian", "microbial"] = "mammalian",
        limit: int = 100,
    ) -> list[Project]:
        """List projects

        Args:
            name: Optional name filter
            project_type: Type of project
            process_format: Process format
            limit: Maximum results

        Returns:
            List of Project objects
        """
        query_params: dict[str, str] = {
            "limit": str(limit),
            "offset": "0",
            "archived": "false",
            "sortBy[createdAt]": "desc",
            "filterBy[processUnitId]": PROCESS_UNIT_MAP[project_type],
            "filterBy[processFormatId]": PROCESS_FORMAT_MAP[process_format],
        }

        if name:
            query_params["filterBy[name]"] = name

        response = self._request("GET", PROJECTS_URL, query_params=query_params)
        data = response.json()

        projects = []
        for item in data:
            projects.append(
                Project(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    project_type=project_type,
                    process_format=process_format,
                )
            )

        return projects

    def get_project(self, project_id: str) -> Project:
        """Get project by ID"""
        try:
            response = self._request("GET", f"{PROJECTS_URL}/{project_id}")
            item = response.json()

            # Resolve project type from process unit ID
            unit_id = item.get("processUnitId")
            project_type = (
                "cultivation"
                if unit_id == PROCESS_UNIT_MAP["cultivation"]
                else "spectroscopy"
            )

            return Project(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                project_type=project_type,
                process_format="mammalian",  # Simplified
            )
        except APIError as e:
            if e.status_code == 404:
                raise EntityNotFoundError("Project not found", entity_type="Project", entity_id=project_id) from e
            raise

    # ========================================================================
    # Model Operations
    # ========================================================================

    def list_models(
        self,
        project: Project | str,
        name: str | None = None,
        model_type: Literal["propagation", "historical"] | None = None,
        limit: int = 100,
    ) -> list[Model]:
        """List models for a project"""
        project_id = project.id if isinstance(project, Project) else project

        query_params: dict[str, str] = {
            "limit": str(limit),
            "offset": "0",
            "archived": "false",
            "filterBy[projectId]": project_id,
        }

        if name:
            query_params["filterBy[name]"] = name

        response = self._request("GET", MODELS_URL, query_params=query_params)
        data = response.json()

        # Simplified model parsing
        models = []
        for item in data:
            # Parse dataset if present
            dataset = None
            if item.get("dataset"):
                dataset = Dataset(
                    id=item["dataset"].get("id", "temp-dataset"),
                    name=item["dataset"].get("name", "Temp Dataset"),
                    description=item["dataset"].get("description", ""),
                    project=project_id,
                    variables=[],
                )

            models.append(
                Model(
                    id=item["id"],
                    name=item["name"],
                    status=item.get("status", "pending"),
                    project=project_id,
                    dataset=dataset,
                    config=item.get("config", {}),
                    model_type=item.get("modelType", "propagation"),
                )
            )

        return models

    def get_model(self, model_id: str) -> Model:
        """Get model by ID"""
        try:
            response = self._request("GET", f"{MODELS_URL}/{model_id}")
            item = response.json()

            # Parse dataset if present
            dataset = None
            project_id = item.get("projectId", item.get("project", {}).get("id", ""))
            if item.get("dataset"):
                dataset = Dataset(
                    id=item["dataset"].get("id", "temp-dataset"),
                    name=item["dataset"].get("name", "Temp Dataset"),
                    description=item["dataset"].get("description", ""),
                    project=project_id,
                    variables=[],
                )

            return Model(
                id=item["id"],
                name=item["name"],
                status=item.get("status", "pending"),
                project=project_id,
                dataset=dataset,
                config=item.get("config", {}),
                model_type=item.get("modelType", "propagation"),
            )
        except APIError as e:
            if e.status_code == 404:
                raise EntityNotFoundError(
                    "Model not found", entity_type="Model", entity_id=model_id
                ) from e
            raise

    # ========================================================================
    # Dataset Operations
    # ========================================================================

    def list_datasets(
        self,
        project: Project | str,
        name: str | None = None,
        limit: int = 100,
    ) -> list[Dataset]:
        """List datasets for a project"""
        project_id = project.id if isinstance(project, Project) else project

        query_params: dict[str, str] = {
            "limit": str(limit),
            "offset": "0",
            "filterBy[projectId]": project_id,
        }

        if name:
            query_params["filterBy[name]"] = name

        response = self._request("GET", DATASETS_URL, query_params=query_params)
        data = response.json()

        datasets = []
        for item in data:
            datasets.append(
                Dataset(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    project=project_id,
                    variables=[],  # Simplified
                    experiments=[],
                )
            )

        return datasets

    # ========================================================================
    # Prediction Operations
    # ========================================================================

    def _predict(
        self,
        model: Model,
        input_data: SpectraPredictionInput
        | PropagationPredictionInput
        | HistoricalPredictionInput,
    ) -> PredictionOutput:
        """Internal prediction method called by Model.predict()

        Handles preprocessing and formatting for all model types.
        """
        # Dispatch to appropriate handler based on input type
        if isinstance(input_data, SpectraPredictionInput):
            return self._predict_spectra(model, input_data)
        elif isinstance(input_data, PropagationPredictionInput):
            return self._predict_cultivation_propagation(model, input_data)
        elif isinstance(input_data, HistoricalPredictionInput):
            return self._predict_cultivation_historical(model, input_data)
        else:
            raise PredictionError(
                f"Unsupported input type: {type(input_data).__name__}",
                input_type=type(input_data).__name__,
            )

    def _predict_spectra(
        self, model: Model, input_data: SpectraPredictionInput
    ) -> PredictionOutput:
        """Handle spectra model predictions"""
        # Validate spectra dimensions
        if not input_data.spectra:
            raise ValidationError(
                "At least one spectrum required", field="spectra", value=[]
            )

        # All spectra must have same dimension
        first_len = len(input_data.spectra[0])
        if not all(len(s) == first_len for s in input_data.spectra):
            raise ValidationError(
                "All spectra must have same dimension",
                field="spectra",
                value="varying lengths",
            )

        # Format instances for API
        instances = []
        for i, spectrum in enumerate(input_data.spectra):
            instance = {"1": spectrum}  # Spectra always in column "1"

            # Add input variables
            if input_data.inputs:
                for var_code, values in input_data.inputs.items():
                    if i < len(values):
                        instance[var_code] = values[i]

            instances.append(instance)

        request_body = {
            "modelId": model.id,
            "instances": instances,
            "config": {"modelConfidence": 80},  # Default confidence
        }

        response = self._request("POST", PREDICT_URL, json_data=request_body)
        return self._format_prediction_response(response.json(), model)

    def _predict_cultivation_propagation(
        self, model: Model, input_data: PropagationPredictionInput
    ) -> PredictionOutput:
        """Handle cultivation propagation model predictions"""
        # Convert timestamps to seconds
        unit_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        multiplier = unit_multipliers[input_data.unit]
        timestamps_seconds = [int(t * multiplier) for t in input_data.timestamps]

        # Validate inputs
        if not input_data.inputs:
            raise ValidationError("Inputs required", field="inputs", value=None)

        # Format instances
        instances = []
        for i, ts in enumerate(timestamps_seconds):
            instance = {"timestamp": ts}

            # Add input values
            for var_code, values in input_data.inputs.items():
                if len(values) == 1:
                    # Initial value (X variables)
                    instance[var_code] = values[0]
                elif i < len(values):
                    # Time-dependent value (W variables, flows)
                    instance[var_code] = values[i]

            instances.append(instance)

        request_body = {
            "modelId": model.id,
            "instances": instances,
            "config": {
                "modelConfidence": input_data.confidence * 100,
                "startingIndex": input_data.starting_index,
            },
        }

        response = self._request("POST", PREDICT_URL, json_data=request_body)
        return self._format_prediction_response(response.json(), model)

    def _predict_cultivation_historical(
        self, model: Model, input_data: HistoricalPredictionInput
    ) -> PredictionOutput:
        """Handle cultivation historical model predictions"""
        # Convert timestamps to seconds
        unit_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        multiplier = unit_multipliers[input_data.unit]
        timestamps_seconds = [int(t * multiplier) for t in input_data.timestamps]

        # Validate steps match timestamps
        if len(input_data.steps) != len(timestamps_seconds):
            raise ValidationError(
                f"Steps length ({len(input_data.steps)}) must match timestamps length ({len(timestamps_seconds)})",
                field="steps",
                value=input_data.steps,
            )

        # Format instances
        instances = []
        for i, (ts, step) in enumerate(zip(timestamps_seconds, input_data.steps, strict=False)):
            instance = {"timestamp": ts, "step": step}

            # Add input values
            for var_code, values in input_data.inputs.items():
                if len(values) == 1:
                    # Initial value
                    instance[var_code] = values[0]
                elif i < len(values):
                    # Time-dependent value
                    instance[var_code] = values[i]

            instances.append(instance)

        request_body = {
            "modelId": model.id,
            "instances": instances,
            "config": {"modelConfidence": input_data.confidence * 100},
        }

        response = self._request("POST", PREDICT_URL, json_data=request_body)
        return self._format_prediction_response(response.json(), model)

    def _format_prediction_response(
        self, response_data: dict, model: Model
    ) -> PredictionOutput:
        """Format API prediction response to PredictionOutput"""
        # Check for error in response
        if "error" in response_data:
            raise PredictionError(response_data["error"], model_id=model.id)

        # Extract predictions (structure may vary by API version)
        predictions = response_data.get("predictions", {})
        outputs = {}

        # Format outputs by variable code
        for var_code, values in predictions.items():
            if isinstance(values, list):
                outputs[var_code] = values
            elif isinstance(values, dict) and "values" in values:
                outputs[var_code] = values["values"]

        # Extract confidence intervals if present
        confidence_intervals = response_data.get("confidenceIntervals")

        return PredictionOutput(
            outputs=outputs,
            confidence_intervals=confidence_intervals,
            metadata={
                "model_id": model.id,
                "model_name": model.name,
                "model_status": model.status,
            },
        )
