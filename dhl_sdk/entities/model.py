# Disable import cycle check: Model and ModelExperiment have bidirectional references
# (Model creates ModelExperiment, ModelExperiment holds Model)
# pyright: reportImportCycles=false
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any
from typing_extensions import override

from dhl_sdk._utils import paginate

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.model import Model as OpenAPIModel
    from openapi_client.models.prediction_response import PredictionResponse
    from openapi_client.models.model_prediction_config import ModelPredictionConfig
    from openapi_client.models.tabularized_data_model_input import TabularizedDataModelInput
    from dhl_sdk.entities.model_variable import ModelVariable
    from dhl_sdk.entities.model_experiment import ModelExperiment


class Model:
    _model: "OpenAPIModel"

    def __init__(self, model: "OpenAPIModel"):
        self._model = model

    @override
    def __str__(self) -> str:
        return f"Model({self.name}, {self.type})"

    @property
    def id(self) -> str:
        return self._model.id

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def description(self) -> str:
        return self._model.description

    @property
    def status(self) -> str:
        return self._model.status.value

    @property
    def type(self) -> str:
        return self._model.type.value

    @property
    def project_id(self) -> str:
        return self._model.project_id

    @property
    def dataset_id(self) -> str | None:
        return self._model.dataset_id

    @property
    def variant(self) -> str:
        return self._model.variant

    @property
    def step_size(self) -> int | None:
        return self._model.step_size

    @property
    def success(self) -> bool:
        """Returns True if model status is 'success'."""
        return self.status == "success"

    def get_variables(self, api: "DefaultApi") -> "Iterator[ModelVariable]":
        """
        Get all variables associated with this model.

        Returns:
            Iterator of ModelVariable objects used in this model
        """
        from dhl_sdk.entities.model_variable import ModelVariable

        for api_model_variable in paginate(
            api.get_model_variables_api_v1_models_model_id_variables_get,
            model_id=self.id,
        ):
            yield ModelVariable(api_model_variable)

    def get_experiments(self, api: "DefaultApi") -> "Iterator[ModelExperiment]":
        """
        Get all experiments used in this model.

        Returns:
            Iterator of ModelExperiment objects used in this model
        """
        from dhl_sdk.entities.model_experiment import ModelExperiment  # type: ignore[attr-defined]

        for api_model_experiment in paginate(
            api.get_model_experiments_api_v1_models_model_id_experiments_get,
            model_id=self.id,
        ):
            yield ModelExperiment(api_model_experiment, self)

    def predict(
        self,
        api: "DefaultApi",
        inputs: dict[str, "TabularizedDataModelInput"],
        timestamps: list[int],
        config: "ModelPredictionConfig | None" = None,
    ) -> "PredictionResponse":
        """
        Make predictions using the model with new OpenAPI format.

        Parameters
        ----------
        api : DefaultApi
            The API client instance
        inputs : dict[str, TabularizedDataModelInput]
            Dictionary mapping variable IDs to input data (scalar or time series)
        timestamps : list[int]
            List of timestamps in seconds (Unix or relative starting from 0)
        config : ModelPredictionConfig | None, optional
            Configuration for prediction (model_confidence, starting_timestamp)

        Returns
        -------
        PredictionResponse
            Response containing predictions keyed by variable ID

        Raises
        ------
        ValueError
            If model is not ready for prediction (status != "success")

        Example
        -------
        >>> from openapi_client.models.numerical_time_series import NumericalTimeSeries
        >>> from openapi_client.models.tabularized_time_series_data import TabularizedTimeSeriesData
        >>> from openapi_client.models.tabularized_data_model_input import TabularizedDataModelInput
        >>> inputs = {
        ...     "var-id-1": TabularizedDataModelInput(TabularizedTimeSeriesData(NumericalTimeSeries(values=[1.0, 2.0, 3.0]))),
        ...     "var-id-2": TabularizedDataModelInput(TabularizedTimeSeriesData(NumericalTimeSeries(values=[4.0, 5.0, 6.0])))
        ... }
        >>> timestamps = [0, 60, 120]
        >>> response = model.predict(api, inputs, timestamps)
        """
        from openapi_client.models.prediction_payload import PredictionPayload

        if not self.success:
            raise ValueError(f"Model '{self.name}' is not ready for prediction. Current status: {self.status}")

        payload = PredictionPayload(inputs=inputs, timestamps=timestamps, config=config)

        return api.model_prediction_api_v1_models_model_id_predict_post(model_id=self.id, prediction_payload=payload)

    def predict_compat(
        self,
        api: "DefaultApi",
        inputs: dict[str, list["Any"]],  # pyright: ignore[reportExplicitAny] - Legacy compat method accepts dynamic untyped data
        timestamps: list[int],
        timestamps_unit: str = "s",
        config: "ModelPredictionConfig | None" = None,
    ) -> dict[str, list["Any"] | None]:  # pyright: ignore[reportExplicitAny] - Legacy compat method returns dynamic untyped data
        """
        Make predictions using legacy format (backwards compatible).

        This method converts legacy input format (variable codes, simple lists) to the new
        OpenAPI format, calls predict(), and converts the response back to legacy format.

        Parameters
        ----------
        api : DefaultApi
            The API client instance
        inputs : dict[str, list]
            Dictionary mapping variable codes to value lists
            - Single-element lists treated as scalars
            - Multi-element lists treated as time series
        timestamps : list[int]
            List of timestamps (Unix or relative starting from 0)
        timestamps_unit : str, optional
            Unit of the timestamps: "s" (seconds), "m" (minutes), "h" (hours), "d" (days)
            Default is "s". Timestamps will be converted to seconds for the API.
        config : ModelPredictionConfig | None, optional
            Configuration for prediction (model_confidence, starting_timestamp)

        Returns
        -------
        dict[str, list]
            Dictionary mapping variable codes to prediction value lists

        Raises
        ------
        ValueError
            If model is not ready for prediction, variable code not found, or invalid timestamps_unit
        NotImplementedError
            If spectrum variables are encountered (not yet supported)

        Example
        -------
        >>> inputs = {
        ...     "Temperature": [25.0, 26.0, 27.0],
        ...     "pH": [7.0]  # Single value becomes scalar
        ... }
        >>> timestamps = [0, 60, 120]
        >>> predictions = model.predict_compat(api, inputs, timestamps, timestamps_unit="s")
        >>> # Returns: {"Glucose": [10.5, 11.2, 12.0], "Lactate": [2.5, 2.7, 2.9]}
        >>>
        >>> # Using different time unit
        >>> timestamps_hours = [0, 1, 2]
        >>> predictions = model.predict_compat(api, inputs, timestamps_hours, timestamps_unit="h")
        """
        from openapi_client.models.numerical_scalar import NumericalScalar
        from openapi_client.models.numerical_time_series import NumericalTimeSeries
        from openapi_client.models.categorical_scalar import CategoricalScalar
        from openapi_client.models.categorical_time_series import CategoricalTimeSeries
        from openapi_client.models.logical_scalar import LogicalScalar
        from openapi_client.models.logical_time_series import LogicalTimeSeries
        from openapi_client.models.scalars_data import ScalarsData
        from openapi_client.models.tabularized_time_series_data import TabularizedTimeSeriesData
        from openapi_client.models.tabularized_data_model_input import TabularizedDataModelInput
        from openapi_client.models.predicted_scalars_data import PredictedScalarsData

        if not self.success:
            raise ValueError(f"Model '{self.name}' is not ready for prediction. Current status: {self.status}")

        # Convert timestamps to seconds based on unit
        unit_to_seconds = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if timestamps_unit not in unit_to_seconds:
            raise ValueError(f"Invalid timestamps_unit '{timestamps_unit}'. Must be one of: s, m, h, d")

        conversion_factor = unit_to_seconds[timestamps_unit]
        timestamps_seconds = [int(t * conversion_factor) for t in timestamps]

        # Get all model variables and create bidirectional mappings
        variables = list(self.get_variables(api))
        code_to_var = {var.code: var for var in variables}
        id_to_var = {var.id: var for var in variables}

        # Convert legacy inputs to OpenAPI format
        openapi_inputs: dict[str, TabularizedDataModelInput] = {}

        for var_code, values in inputs.items():
            if var_code not in code_to_var:
                raise ValueError(f"Variable code '{var_code}' not found in model variables")

            var = code_to_var[var_code]
            variant = var.variant

            # Check for unsupported variants
            if variant == "spectrum":
                raise NotImplementedError("Spectrum variables are not yet supported in predict_compat")

            # Determine if scalar or time series based on input length
            is_scalar = len(values) == 1

            # Create appropriate data type based on variant
            if variant in ("numeric", "flow"):
                # Numeric/flow variables
                if is_scalar:
                    data_instance = NumericalScalar(value=values[0])  # pyright: ignore[reportAny] - Legacy compat accepts list[Any], runtime type validated by Pydantic
                    openapi_inputs[var.id] = TabularizedDataModelInput(ScalarsData(data_instance))
                else:
                    data_instance = NumericalTimeSeries(values=values)
                    openapi_inputs[var.id] = TabularizedDataModelInput(TabularizedTimeSeriesData(data_instance))

            elif variant == "categorical":
                # Categorical variables
                if is_scalar:
                    data_instance = CategoricalScalar(value=values[0])  # pyright: ignore[reportAny] - Legacy compat accepts list[Any], runtime type validated by Pydantic
                    openapi_inputs[var.id] = TabularizedDataModelInput(ScalarsData(data_instance))
                else:
                    data_instance = CategoricalTimeSeries(values=values)
                    openapi_inputs[var.id] = TabularizedDataModelInput(TabularizedTimeSeriesData(data_instance))

            elif variant == "logical":
                # Logical variables
                if is_scalar:
                    data_instance = LogicalScalar(value=values[0])  # pyright: ignore[reportAny] - Legacy compat accepts list[Any], runtime type validated by Pydantic
                    openapi_inputs[var.id] = TabularizedDataModelInput(ScalarsData(data_instance))
                else:
                    data_instance = LogicalTimeSeries(values=values)
                    openapi_inputs[var.id] = TabularizedDataModelInput(TabularizedTimeSeriesData(data_instance))

            else:
                # Default to numeric for unknown variants
                if is_scalar:
                    data_instance = NumericalScalar(value=values[0])  # pyright: ignore[reportAny] - Legacy compat accepts list[Any], runtime type validated by Pydantic
                    openapi_inputs[var.id] = TabularizedDataModelInput(ScalarsData(data_instance))
                else:
                    data_instance = NumericalTimeSeries(values=values)
                    openapi_inputs[var.id] = TabularizedDataModelInput(TabularizedTimeSeriesData(data_instance))

        # Call the new predict method with converted timestamps
        response = self.predict(api, openapi_inputs, timestamps_seconds, config)

        # Convert response back to legacy format (code -> values list or None)
        result: dict[str, list["Any"] | None] = {}  # pyright: ignore[reportExplicitAny] - Legacy compat method returns dynamic untyped data

        for var_id, predicted_data in response.predictions.items():
            if var_id not in id_to_var:
                continue  # Skip variables not in our mapping

            var_code = id_to_var[var_id].code
            actual = predicted_data.actual_instance

            # Extract values based on oneOf type
            if actual is None:
                result[var_code] = None
            elif isinstance(actual, PredictedScalarsData):
                # Scalar: wrap value in list
                inner = actual.actual_instance
                result[var_code] = [inner.value] if inner else None
            else:
                # Time series: use values as-is (with safety check)
                # Type checker knows this must be PredictedTimeSeriesData after None and PredictedScalarsData checks
                inner = actual.actual_instance
                result[var_code] = inner.values if inner else None

        return result
