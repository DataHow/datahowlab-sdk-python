"""
Example: Model predictions using type-safe data format

Demonstrates using predict() with OpenAPI native types.
This format is more verbose but provides full type safety.
"""

from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from openapi_client.models.model_type import ModelType
from openapi_client.models.tabularized_data_model_input import TabularizedDataModelInput
from openapi_client.models.tabularized_time_series_data import TabularizedTimeSeriesData
from openapi_client.models.scalars_data import ScalarsData
from openapi_client.models.numerical_time_series import NumericalTimeSeries
from openapi_client.models.numerical_scalar import NumericalScalar
from example_config import DHL_BASE_URL, DHL_PROJECT  # pyright: ignore[reportMissingImports] - examples are standalone scripts, not a package

# Initialize the client
key = APIKeyAuthentication()
client = DataHowLabClient(auth_key=key, base_url=DHL_BASE_URL)

# Get the project
projects = client.get_projects(name=DHL_PROJECT)
project = next(projects)

# Find a successful propagation model
models = [m for m in project.get_models(model_type=ModelType.PROPAGATION) if m.success]
if not models:
    raise ValueError("No successful propagation models found")
model = models[0]

# Get first experiment from the model
model_exp = next(model.get_experiments())

# Get experiment data in type-safe format
exp_data = model_exp.get_data()

# Get model variables to determine input types
model_vars = list(model.get_variables())
input_vars = [v for v in model_vars if v.input_type != "none"]

# Build inputs dict: {variable_id: TabularizedDataModelInput}
# The input format depends on whether the model expects scalar or timeseries inputs
inputs: dict[str, TabularizedDataModelInput] = {}

for var in input_vars:
    if var.id not in exp_data.data:
        continue

    var_data = exp_data.data[var.id]

    # Extract the actual data from the oneOf wrapper
    # Structure: TabularizedDataModelOutput -> (TabularizedTimeSeriesData | ScalarsData) -> inner type
    actual = var_data.actual_instance
    if not actual:
        continue

    # Handle scalar vs timeseries inputs differently
    if var.input_type == "scalar":
        # For scalar inputs, convert timeseries to scalar by taking first value
        if isinstance(actual, TabularizedTimeSeriesData):
            inner = actual.actual_instance
            if isinstance(inner, NumericalTimeSeries):
                # Extract first value and wrap in scalar types
                scalar_value = inner.values[0]
                scalar = NumericalScalar(value=scalar_value)
                scalar_data = ScalarsData(actual_instance=scalar)
                inputs[var.id] = TabularizedDataModelInput(actual_instance=scalar_data)
            else:
                # Non-numerical time series - skip
                inputs[var.id] = TabularizedDataModelInput(actual_instance=None)
        else:
            # Already a scalar - use as is
            inputs[var.id] = TabularizedDataModelInput(actual_instance=actual)
    else:
        # Timeseries input - use the data as is
        inputs[var.id] = TabularizedDataModelInput(actual_instance=actual)

# Make prediction using type-safe format
# Returns: PredictionResult with predictions dict
predictions = model.predict(inputs=inputs, timestamps=exp_data.timestamps, config=None)

# Process predictions
# Structure: predictions.predictions -> dict[var_id, PredictedDataModelOutput]
# PredictedDataModelOutput -> PredictedTimeSeriesData -> inner timeseries type
var_id_to_code = {v.id: v.code for v in model_vars}

for var_id, predicted_data in predictions.predictions.items():
    var_code = var_id_to_code.get(var_id, var_id)

    # Extract predicted values from nested structure
    actual = predicted_data.actual_instance
    if not actual or not isinstance(actual, PredictedTimeSeriesData):
        continue

    inner = actual.actual_instance
    if not inner:
        continue

    predicted_values = inner.values

    # Compare with actual values from experiment
    if var_id in exp_data.data:
        actual_data = exp_data.data[var_id]
        actual_inst = actual_data.actual_instance
        if isinstance(actual_inst, TabularizedTimeSeriesData):
            actual_inner = actual_inst.actual_instance
            if actual_inner:
                actual_values = actual_inner.values
                # Process predictions vs actuals...
                pass
