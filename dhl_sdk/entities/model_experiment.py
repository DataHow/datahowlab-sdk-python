from collections.abc import Iterator
from typing import TYPE_CHECKING, Any
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

    @property
    def tags(self) -> dict[str, str]:
        """
        Tags associated with the model experiment.

        Returns
        -------
        dict[str, str]
            Dictionary of tag key-value pairs. Returns empty dict if no tags.
        """
        return self._model_experiment.tags or {}

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
        from openapi_client.models.scalars_data import ScalarsData

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
            actual = tabularized_output.actual_instance

            # Extract values based on oneOf type
            if actual is None:
                result[var_code] = {"values": [None], "timestamps": [0]}
            elif isinstance(actual, ScalarsData):
                # Scalar: convert to timeseries with timestamps=[0]
                inner = actual.actual_instance
                value = inner.value if inner else None
                result[var_code] = {"values": [value], "timestamps": [0]}
            else:
                # Time series: use top-level timestamps
                # Type checker knows this must be TabularizedTimeSeriesData after None and ScalarsData checks
                inner = actual.actual_instance
                values = inner.values if inner else [None]
                result[var_code] = {"values": values, "timestamps": top_level_timestamps}

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
