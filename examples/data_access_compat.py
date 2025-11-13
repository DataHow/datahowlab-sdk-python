#!/usr/bin/env python3
"""
Example: Accessing data using compatibility format

Demonstrates data access with get_data_compat() which returns simple Python dicts.
"""

from dhl_sdk import DataHowLabClient, APIKeyAuthentication


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

    # Get experiment data in compatibility format
    # Returns: {variable_code: {"values": [...], "timestamps": [...]}}
    exp_data = model_exp.get_data_compat()
    print(f"  Variables: {len(exp_data)}")

    # Show sample data for first variable
    first_var_code = list(exp_data.keys())[0]
    first_var_data = exp_data[first_var_code]
    if first_var_data and first_var_data.get("values"):
        print(f"  First variable: {first_var_code}")
        print(f"    Values: {len(first_var_data['values'])}")
        print(f"    First value: {first_var_data['values'][0]}")
        print(f"    Last value: {first_var_data['values'][-1]}")

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
