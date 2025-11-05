from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, cast
from typing_extensions import override

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.model_experiment import ModelExperiment as OpenAPIModelExperiment
    from openapi_client.models.tabularized_experiment_data import TabularizedExperimentData
    from dhl_sdk.entities.product import Product
    from dhl_sdk.entities.model import Model
    from dhl_sdk.entities.model_variable import ModelVariable


class ModelExperiment:
    _model_experiment: "OpenAPIModelExperiment"
    _model: "Model"

    def __init__(self, model_experiment: "OpenAPIModelExperiment", model: "Model"):
        self._model_experiment = model_experiment
        self._model = model

    @override
    def __str__(self) -> str:
        return f"ModelExperiment({self._model_experiment.display_name})"

    @property
    def id(self) -> str:
        return self._model_experiment.id

    @property
    def display_name(self) -> str:
        return self._model_experiment.display_name

    @property
    def product_id(self) -> str:
        return self._model_experiment.product_id

    @property
    def description(self) -> str:
        return self._model_experiment.description

    @property
    def start_time(self) -> str | None:
        return self._model_experiment.start_time

    @property
    def variant(self) -> str:
        return self._model_experiment.variant.value

    @property
    def used_for_training(self) -> bool | None:
        return self._model_experiment.used_for_training

    def get_data(self, api: "DefaultApi") -> "TabularizedExperimentData":
        """
        Retrieve experiment data in tabularized format.

        Returns:
            TabularizedExperimentData with shared timestamps at top level and data per variable
        """
        return api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get(
            model_id=self._model.id, experiment_id=self.id
        )

    def get_data_compat(self, api: "DefaultApi") -> dict[str, dict[str, Any]]:  # pyright: ignore[reportExplicitAny] - Legacy compatibility method returns dynamic untyped data
        """
        Retrieve experiment data in compat format (legacy format).

        This method converts the tabularized data format to the legacy format where:
        - Timeseries variables get their timestamps from the top-level timestamps array
        - Scalar variables are converted to timeseries with timestamps=[0]
        - Data is keyed by variable code instead of variable ID

        Returns:
            Dict with variable codes as keys and {"values": [...], "timestamps": [...]} as values
        """
        raw_data = self.get_data(api)
        variables = self.get_variables(api)

        # Create a mapping from variable ID to variable
        var_id_to_var = {var.id: var for var in variables}

        result: dict[str, dict[str, Any]] = {}  # pyright: ignore[reportExplicitAny] - Legacy compatibility method returns dynamic untyped data
        top_level_timestamps = raw_data.timestamps

        for var_id, tabularized_output in raw_data.data.items():
            var = var_id_to_var.get(var_id)
            if not var:
                continue

            var_code = var.code
            output_dict = cast(Any, tabularized_output.to_dict() if hasattr(tabularized_output, "to_dict") else tabularized_output)  # pyright: ignore[reportExplicitAny, reportAny] - OpenAPI oneOf types require dynamic handling

            # Handle the actual_instance within TabularizedDataModelOutput
            if isinstance(output_dict, dict) and "actual_instance" in output_dict:
                actual_data = cast(dict[str, Any], output_dict["actual_instance"])  # pyright: ignore[reportExplicitAny] - OpenAPI oneOf actual_instance has dynamic structure
            else:
                actual_data = cast(dict[str, Any], output_dict)  # pyright: ignore[reportExplicitAny] - OpenAPI oneOf types have dynamic structure

            # Check if it's a scalar or timeseries
            if isinstance(actual_data, dict):  # pyright: ignore[reportUnnecessaryIsInstance] - Runtime check needed due to cast from Any
                data_format = actual_data.get("format")

                if data_format == "scalar":
                    # Convert scalar to timeseries with timestamps=[0]
                    value = actual_data.get("value")
                    result[var_code] = {"values": [value], "timestamps": [0]}
                elif data_format == "timeseries":
                    # Use top-level timestamps for timeseries
                    values = actual_data.get("values", [])  # pyright: ignore[reportAny] - Dynamic data structure from OpenAPI oneOf
                    result[var_code] = {"values": values, "timestamps": top_level_timestamps}
                else:
                    # Unknown format, pass through
                    result[var_code] = actual_data
            else:
                # If not a dict, pass through as-is
                result[var_code] = cast(dict[str, Any], actual_data)  # pyright: ignore[reportExplicitAny] - Unknown format fallback for legacy compatibility

        return result

    def get_variables(self, api: "DefaultApi") -> "Iterator[ModelVariable]":
        """Get all variables associated with this model experiment."""
        # Delegate to the Model's get_variables method
        return self._model.get_variables(api)

    def get_product(self, api: "DefaultApi") -> "Product":
        """Get the product associated with this model experiment."""
        from dhl_sdk.entities.product import Product

        api_product = api.get_product_by_id_api_v1_products_product_id_get(product_id=self.product_id)
        return Product(api_product)
