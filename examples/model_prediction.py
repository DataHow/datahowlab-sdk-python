#!/usr/bin/env python3
"""
Example: Model predictions using OpenAPI format

Demonstrates using predict() with get_data() (OpenAPI native format).
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


def main():
    # Initialize client
    key = APIKeyAuthentication()
    client = DataHowLabClient(auth_key=key, base_url="https://dev.datahowlab.ch/")

    # Get the SDK Test TM project
    projects = client.get_projects(name="SDK Test TM")
    project = next(projects)

    # Find a successful propagation model
    models = [m for m in project.get_models(model_type=ModelType.PROPAGATION) if m.success]
    model = models[0]
    print(f"Model: {model.name}")

    # Get experiment from the model
    model_experiments = list(model.get_experiments())
    model_exp = model_experiments[0]

    # Get experiment data in OpenAPI format (TabularizedExperimentData)
    exp_data = model_exp.get_data()
    print(f"Experiment: {model_exp.display_name}")
    print(f"  Timestamps: {len(exp_data.timestamps)}")
    print(f"  Variables: {len(exp_data.data)}")

    # Get model variables to determine input types
    model_vars = list(model.get_variables())
    input_vars = [v for v in model_vars if v.input_type != "none"]

    # Build inputs dict: {variable_id: TabularizedDataModelInput}
    inputs: dict[str, TabularizedDataModelInput] = {}

    for var in input_vars:
        if var.id not in exp_data.data:
            continue

        var_data = exp_data.data[var.id]

        # Structure: TabularizedDataModelOutput -> (TabularizedTimeSeriesData | ScalarsData) -> inner data
        actual = var_data.actual_instance
        if not actual:
            continue

        # Check if this variable needs scalar or timeseries input
        if var.input_type == "scalar":
            # For scalar inputs, extract first value from timeseries or use scalar value
            if isinstance(actual, TabularizedTimeSeriesData):
                inner = actual.actual_instance
                if not isinstance(inner, NumericalTimeSeries):
                    # Assume that there are no categorical and logical time series
                    inputs[var.id] = TabularizedDataModelInput(actual_instance=None)
                else:
                    # Numerical time series - take first value as scalar
                    scalar_value = inner.values[0]
                    scalar = NumericalScalar(value=scalar_value)
                    scalar_data = ScalarsData(actual_instance=scalar)
                    inputs[var.id] = TabularizedDataModelInput(actual_instance=scalar_data)
            else:
                # Already a scalar
                inputs[var.id] = TabularizedDataModelInput(actual_instance=actual)
        else:
            inputs[var.id] = TabularizedDataModelInput(actual_instance=actual)

    print(f"  Prepared {len(inputs)} inputs")
    print(f"    Scalars: {sum(1 for v in input_vars if v.input_type == 'scalar' and v.id in inputs)}")
    print(f"    Timeseries: {sum(1 for v in input_vars if v.input_type != 'scalar' and v.id in inputs)}")

    # Make prediction using OpenAPI format
    print("\nMaking prediction...")
    predictions = model.predict(inputs=inputs, timestamps=exp_data.timestamps, config=None)

    print(f"✓ Prediction successful!\n")

    # Display results
    print("Predictions:")

    # Create mapping from variable ID to code for output
    var_id_to_code = {v.id: v.code for v in model_vars}

    for var_id, predicted_data in predictions.predictions.items():
        var_code = var_id_to_code.get(var_id, var_id)

        # Extract predicted values from nested structure
        actual = predicted_data.actual_instance
        if not actual:
            continue

        if not isinstance(actual, PredictedTimeSeriesData):
            continue

        inner = actual.actual_instance
        if not inner:
            continue

        # Get predicted values
        predicted_values = inner.values

        if predicted_values and len(predicted_values) > 0:
            # Get actual values for comparison from experiment data
            if var_id in exp_data.data:
                actual_data = exp_data.data[var_id]
                actual_inst = actual_data.actual_instance
                if isinstance(actual_inst, TabularizedTimeSeriesData):
                    actual_inner = actual_inst.actual_instance
                    if actual_inner:
                        actual_values = actual_inner.values

                        print(f"  {var_code}:")
                        print(f"    Predicted: {predicted_values[0]:.2f} -> {predicted_values[-1]:.2f}")
                        print(f"    Actual:    {actual_values[0]:.2f} -> {actual_values[-1]:.2f}")


if __name__ == "__main__":
    main()
