"""
Example: Accessing data using legacy data format

Demonstrates data access with get_data_compat() which returns simple Python dicts.
This is the recommended format for most users as it's easier to work with.
"""

from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from example_config import DHL_BASE_URL, DHL_PROJECT  # pyright: ignore[reportMissingImports] - examples are standalone scripts, not a package

# Initialize the client with API key authentication
key = APIKeyAuthentication()
client = DataHowLabClient(auth_key=key, base_url=DHL_BASE_URL)

# Get the project by name
projects = client.get_projects(name=DHL_PROJECT)
project = next(projects)

# Get first model from the project
models = list(project.get_models())
model = models[0]

# Get first experiment from the model
model_exp = next(model.get_experiments())

# Get experiment data in legacy format
# Returns a simple dict: {variable_code: {"values": [...], "timestamps": [...]}}
# This format is much easier to work with than the type-safe format
exp_data = model_exp.get_data_compat()

# Access data for a specific variable by code
for var_code, var_data in exp_data.items():
    if var_data and var_data.get("values"):
        values = var_data["values"]  # pyright: ignore[reportAny]
        timestamps = var_data["timestamps"]  # pyright: ignore[reportAny]
        # Process the time series data...
        break

# Get related entities
exp_product = model_exp.get_product()
exp_variables = list(model_exp.get_variables())

# Filter models by success status
successful_models = [m for m in models if m.success]
