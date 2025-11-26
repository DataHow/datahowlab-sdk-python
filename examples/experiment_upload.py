"""
Example: Creating an experiment using type-safe data format

Demonstrates uploading experiment data using raw OpenAPI types directly.
This format is more verbose but provides full type safety.

The data structure uses nested oneOf wrappers:
- RawExperimentDataInputValue wraps RawTimeSeriesData or RawScalarsData
- RawTimeSeriesData wraps specific types like NumericalTimeSeriesWithTimestamps
"""

import random
import string
from datetime import datetime, timezone
from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from dhl_sdk.entities.variable import Variable, VariableRequest
from dhl_sdk.entities.experiment import ExperimentRequest
from openapi_client.models.process_unit_code import ProcessUnitCode
from openapi_client.models.run_details import RunDetails
from openapi_client.models.variantdetails import Variantdetails
from openapi_client.models.numeric_details import NumericDetails
from openapi_client.models.variantdetails1 import Variantdetails1
from openapi_client.models.numerical_time_series_with_timestamps import NumericalTimeSeriesWithTimestamps
from openapi_client.models.raw_time_series_data import RawTimeSeriesData
from openapi_client.models.raw_experiment_data_input_value import RawExperimentDataInputValue
from example_config import DHL_BASE_URL, DHL_PROJECT  # pyright: ignore[reportMissingImports] - examples are standalone scripts, not a package


def random_suffix(length: int = 6):
    """Generate random alphanumeric suffix for unique naming."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# Initialize the client
key = APIKeyAuthentication()
client = DataHowLabClient(auth_key=key, base_url=DHL_BASE_URL)

# Generate unique suffix
suffix = random_suffix()

# Get the project
projects = client.get_projects(name=DHL_PROJECT)
project = next(projects)

# Get an existing product
products = list(client.get_products(search="ORIG"))[:1]
if not products:
    raise ValueError("No product found. Please create one first.")
product = products[0]

# Fetch existing variables by code and group
required_vars = [
    ("Volume", "Z"),
    ("VCD", "X"),
    ("Glc", "X"),
    ("Gln", "X"),
    ("Temp", "W"),
    ("pH", "W"),
]

variables: list[Variable] = []
for code, group_code in required_vars:
    vars_list = list(client.get_variables(code=code, group_code=group_code))
    if not vars_list:
        raise ValueError(f"Variable '{code}' in group '{group_code}' not found")
    var = vars_list[0]
    variables.append(var)

# Create a new Y variable (CQA)
cqa_code = f"CQA-{suffix}"
cqa_request = VariableRequest.new(
    code=cqa_code,
    name=f"Critical Quality Attribute {suffix}",
    description="CQA created via SDK example",
    measurement_unit="mg/L",
    group="Y",
    variant_details=Variantdetails1(actual_instance=NumericDetails(min=0.0, max=100.0)),
    tags={"sdk-example": "true"},
)
cqa_var = cqa_request.create(client)
variables.append(cqa_var)

# Prepare experiment data using type-safe format
# Format: {variable_id: RawExperimentDataInputValue}
start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
timestamps = [
    int(start_time.timestamp()),
    int(start_time.timestamp()) + 86400,  # +1 day
    int(start_time.timestamp()) + 172800,  # +2 days
]

experiment_data: dict[str, RawExperimentDataInputValue] = {}

# Each variable requires wrapping in the correct type-safe types:
# values/timestamps -> NumericalTimeSeriesWithTimestamps
# -> wrapped in RawTimeSeriesData
# -> wrapped in RawExperimentDataInputValue

# Volume (Z) - scalar value
volume_ts = NumericalTimeSeriesWithTimestamps(values=[1.0], timestamps=[timestamps[0]])
experiment_data[variables[0].id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=volume_ts))

# VCD (X) - time series
vcd_ts = NumericalTimeSeriesWithTimestamps(values=[0.5, 1.2, 2.1], timestamps=timestamps)
experiment_data[variables[1].id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=vcd_ts))

# Glc (X) - time series
glc_ts = NumericalTimeSeriesWithTimestamps(values=[25.0, 15.0, 5.0], timestamps=timestamps)
experiment_data[variables[2].id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=glc_ts))

# Gln (X) - time series
gln_ts = NumericalTimeSeriesWithTimestamps(values=[4.0, 2.5, 1.0], timestamps=timestamps)
experiment_data[variables[3].id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=gln_ts))

# Temp (W) - constant value
temp_ts = NumericalTimeSeriesWithTimestamps(values=[37.0, 37.0, 37.0], timestamps=timestamps)
experiment_data[variables[4].id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=temp_ts))

# pH (W) - time series
ph_ts = NumericalTimeSeriesWithTimestamps(values=[7.0, 7.1, 7.05], timestamps=timestamps)
experiment_data[variables[5].id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=ph_ts))

# CQA (Y) - output time series
cqa_ts = NumericalTimeSeriesWithTimestamps(values=[10.0, 25.0, 45.0], timestamps=timestamps)
experiment_data[variables[6].id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=cqa_ts))

# Create experiment with run details
variant_details = Variantdetails(
    actual_instance=RunDetails(
        startTime=start_time.isoformat().replace("+00:00", "Z"),
        endTime=datetime(2024, 1, 5, 10, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
    )
)

experiment_request = ExperimentRequest.new(
    name=f"SDK-Example-{suffix}",
    description="Experiment created via SDK using type-safe data format",
    product=product,
    process_unit=ProcessUnitCode.BR,
    variant_details=variant_details,
    data=experiment_data,
    tags={"sdk-example": "true"},
)

# Submit the experiment
experiment = experiment_request.create(client)

# Verify by retrieving data back
retrieved_data_compat = experiment.get_data_compat()

# Resources created:
# - Variable: cqa_var.code
# - Experiment: experiment.display_name
# Clean up with: python examples/cleanup.py
