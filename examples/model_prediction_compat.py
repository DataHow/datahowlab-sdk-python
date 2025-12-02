"""
Example: Model predictions using legacy data format

Demonstrates using predict_compat() with simple dict inputs and outputs.
This is the recommended approach for most users.
"""

from typing import Any
from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from openapi_client.models.model_type import ModelType
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

# Get first experiment from the model to use as input data
model_experiments = list(model.get_experiments())
model_exp = model_experiments[0]
exp_data = model_exp.get_data_compat()

# Prepare inputs from experiment data
# Only include variables that are model inputs (not outputs)
model_vars = list(model.get_variables())
input_vars = [v for v in model_vars if v.input_type != "none"]

# Build inputs dict: {variable_code: [values]}
inputs: dict[str, list[Any]] = {}  # pyright: ignore[reportExplicitAny]
timestamps: list[int] = []
for var in input_vars:
    if var.code in exp_data and exp_data[var.code]:
        data = exp_data[var.code]
        inputs[var.code] = data["values"]
        # Get timestamps from first variable
        if not timestamps:
            timestamps = data["timestamps"]  # pyright: ignore[reportAny]

# Make prediction using legacy format
# Returns: {variable_code: [predicted_values]}
predictions = model.predict_compat(
    inputs=inputs,
    timestamps=timestamps,
    timestamps_unit="s",
)

# Compare predictions with actual values
for var_code, predicted_values in predictions.items():
    if predicted_values and len(predicted_values) > 0:
        actual_values = exp_data.get(var_code, {}).get("values", [])  # pyright: ignore[reportAny]
        if actual_values:
            # Process predictions vs actuals...
            pass
