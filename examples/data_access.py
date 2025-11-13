#!/usr/bin/env python3
"""
Example: Accessing data using OpenAPI format

Demonstrates how to retrieve and work with data using the native OpenAPI format.
"""

from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from openapi_client.models.numerical_time_series import NumericalTimeSeries


def main():
    # Initialize client
    key = APIKeyAuthentication()
    client = DataHowLabClient(auth_key=key, base_url="https://dev.datahowlab.ch/")

    # Get the SDK Test TM project
    projects = client.get_projects(name="SDK Test TM")
    project = next(projects)
    print(f"Project: {project.name}")

    # Get models to access their experiments
    models = list(project.get_models())
    model = models[0]
    print(f"Model: {model.name}")

    # Get experiments from the model
    model_experiments = list(model.get_experiments())
    if not model_experiments:
        print("No experiments found")
        return

    model_exp = model_experiments[0]
    print(f"\nExperiment: {model_exp.display_name}")
    print(f"  Product ID: {model_exp.product_id}")

    # Get experiment data in OpenAPI format (TabularizedExperimentData)
    exp_data = model_exp.get_data()
    print(f"\nExperiment data (OpenAPI format):")
    print(f"  Type: {type(exp_data).__name__}")
    print(f"  Timestamps: {len(exp_data.timestamps)}")
    print(f"  Variables: {len(exp_data.data)}")

    # Access data for first variable
    first_var_id = list(exp_data.data.keys())[0]
    var_data = exp_data.data[first_var_id]

    print(f"\nFirst variable (ID: {first_var_id[:8]}...):")
    print(f"  Type: {type(var_data).__name__}")

    # Extract actual data from nested oneOf structure
    # Structure: TabularizedDataModelOutput -> TabularizedTimeSeriesData -> NumericalTimeSeries
    actual = var_data.actual_instance
    if actual:
        inner = actual.actual_instance
        if inner and isinstance(inner, NumericalTimeSeries):
            print(f"    Data type: {inner.type}")
            print(f"    Format: {inner.format}")
            print(f"    Values: {len(inner.values)}")
            print(f"    First value: {inner.values[0]}")
            print(f"    Last value: {inner.values[-1]}")

    # Get related entities
    print(f"\nRelated entities:")

    # Get product
    exp_product = model_exp.get_product()
    print(f"  Product: {exp_product.code} - {exp_product.name}")

    # Get variables (from model)
    exp_variables = list(model_exp.get_variables())
    print(f"  Variables: {len(exp_variables)} total")
    for var in exp_variables[:3]:
        print(f"    - {var.code}: {var.name}")
    if len(exp_variables) > 3:
        print(f"    ... and {len(exp_variables) - 3} more")

    # Access models in the project
    print(f"\nModels in project:")
    successful_models = [m for m in models if m.success]
    print(f"  Total: {len(models)}")
    print(f"  Successful: {len(successful_models)}")

    for m in successful_models[:3]:
        print(f"    - {m.name} ({m.type})")


if __name__ == "__main__":
    main()
