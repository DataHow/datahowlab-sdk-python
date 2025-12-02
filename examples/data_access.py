"""
Example: Accessing data using type-safe data format

Demonstrates retrieving and working with experiment data using native OpenAPI types.
This format provides full type safety but requires more verbose code.
"""

from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from openapi_client.models.numerical_time_series import NumericalTimeSeries
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

# Get experiment data in type-safe format
# Returns: TabularizedExperimentData with timestamps and nested data structure
exp_data = model_exp.get_data()

# The data is structured as:
# - exp_data.timestamps: list of Unix timestamps
# - exp_data.data: dict mapping variable_id -> TabularizedDataModelOutput
#
# TabularizedDataModelOutput is a oneOf wrapper that contains:
#   - TabularizedTimeSeriesData (for time series)
#   - ScalarsData (for scalar values)
#
# Each of these is also a oneOf wrapper for specific types like:
#   - NumericalTimeSeries
#   - CategoricalTimeSeries
#   - LogicalTimeSeries
#   - NumericalScalar, etc.

# Access data for first variable
first_var_id = list(exp_data.data.keys())[0]
var_data = exp_data.data[first_var_id]

# Extract actual data from nested oneOf structure
actual = var_data.actual_instance
if actual:
    inner = actual.actual_instance
    if inner and isinstance(inner, NumericalTimeSeries):
        # Now we have the actual numerical time series data
        values = inner.values
        # Use the values for further processing...

# Get related entities for the experiment
exp_product = model_exp.get_product()
exp_variables = list(model_exp.get_variables())

# Filter models by success status
successful_models = [m for m in models if m.success]
