#!/usr/bin/env python3
"""
Example: Making predictions with DataHowLab models

Demonstrates how to use a trained propagation model to make predictions.
"""

from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from openapi_client.models.model_type import ModelType


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
    exp_data = model_exp.get_data_compat()
    print(f"Experiment: {model_exp.display_name}")

    # Prepare inputs from experiment data
    model_vars = list(model.get_variables())
    input_vars = [v for v in model_vars if v.input_type != "none"]

    inputs = {}
    timestamps = []
    for var in input_vars:
        if var.code in exp_data and exp_data[var.code]:
            data = exp_data[var.code]
            inputs[var.code] = data["values"]  # pyright: ignore[reportAny]
            if not timestamps:
                timestamps = data["timestamps"]  # pyright: ignore[reportAny]

    # Make prediction
    predictions = model.predict_compat(
        inputs=inputs,
        timestamps=timestamps,  # pyright: ignore[reportArgumentType]
        timestamps_unit="s",
    )

    # Display results
    print(f"\nPredictions:")
    for var_code, predicted_values in predictions.items():
        if predicted_values and len(predicted_values) > 0:
            actual_values = exp_data.get(var_code, {}).get("values", [])
            if actual_values:
                print(f"  {var_code}:")
                print(f"    Predicted: {predicted_values[0]:.2f} -> {predicted_values[-1]:.2f}")
                print(f"    Actual:    {actual_values[0]:.2f} -> {actual_values[-1]:.2f}")


if __name__ == "__main__":
    main()
