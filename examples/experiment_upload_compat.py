"""
Example: Creating an experiment using legacy data format

Demonstrates the recommended approach for uploading experiment data:
1. Fetch existing variables by code and group
2. Create a new Y variable (CQA) with constraints
3. Prepare data in simple dict format: {code: {values: [...], timestamps: [...]}}
4. Convert to type-safe format using ExperimentRequest.from_compat_data()
5. Create the experiment

This format is easier to work with than raw type-safe types.
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
from example_config import DHL_BASE_URL, DHL_PROJECT  # pyright: ignore[reportMissingImports] - examples are standalone scripts, not a package


def random_suffix(length: int = 6):
    """Generate random alphanumeric suffix for unique naming."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# Initialize the client
key = APIKeyAuthentication()
client = DataHowLabClient(auth_key=key, base_url=DHL_BASE_URL)

# Generate unique suffix for this example run
suffix = random_suffix()

# Get the project
projects = client.get_projects(name=DHL_PROJECT)
project = next(projects)

# Get an existing product to associate with the experiment
products = list(client.get_products(search="ORIG"))[:1]
if not products:
    raise ValueError("No product found. Please create one first.")
product = products[0]

# Fetch existing variables by code and group
# This is the recommended way to find variables for your experiment
required_vars = [
    ("Volume", "Z"),  # Z group: experiment-level parameters
    ("VCD", "X"),  # X group: inputs
    ("Glc", "X"),
    ("Gln", "X"),
    ("Temp", "W"),  # W group: environmental parameters
    ("pH", "W"),
]

variables: list[Variable] = []
for code, group_code in required_vars:
    vars_list = list(client.get_variables(code=code, group_code=group_code))
    if not vars_list:
        raise ValueError(f"Variable '{code}' in group '{group_code}' not found")
    var = vars_list[0]
    variables.append(var)

# Create a new Y variable (output/CQA) for this experiment
cqa_code = f"CQA-{suffix}"
cqa_request = VariableRequest.new(
    code=cqa_code,
    name=f"Critical Quality Attribute {suffix}",
    description="CQA created via SDK example",
    measurement_unit="mg/L",
    group="Y",  # Y group: outputs/targets
    variant_details=Variantdetails1(actual_instance=NumericDetails(min=0.0, max=100.0)),
    tags={"sdk-example": "true"},  # Tag for easy cleanup
)
cqa_var = cqa_request.create(client)
variables.append(cqa_var)

# Prepare experiment data in legacy format
# Format: {variable_code: {"values": [...], "timestamps": [...]}}
start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
timestamps = [
    int(start_time.timestamp()),
    int(start_time.timestamp()) + 86400,  # +1 day
    int(start_time.timestamp()) + 172800,  # +2 days
]

compat_data = {
    "Volume": {"values": [1.0], "timestamps": [timestamps[0]]},  # Scalar value
    "VCD": {"values": [0.5, 1.2, 2.1], "timestamps": timestamps},  # Time series
    "Glc": {"values": [25.0, 15.0, 5.0], "timestamps": timestamps},
    "Gln": {"values": [4.0, 2.5, 1.0], "timestamps": timestamps},
    "Temp": {"values": [37.0, 37.0, 37.0], "timestamps": timestamps},  # Constant value
    "pH": {"values": [7.0, 7.1, 7.05], "timestamps": timestamps},
    cqa_code: {"values": [10.0, 25.0, 45.0], "timestamps": timestamps},  # Output
}

# Convert legacy format to type-safe format
# This handles all the complex nested type wrapping automatically
openapi_data = ExperimentRequest.from_compat_data(variables, compat_data)  # pyright: ignore[reportArgumentType] - compat_data is dynamically typed dict, validated at runtime

# Create the experiment with run details (start/end time)
variant_details = Variantdetails(
    actual_instance=RunDetails(
        startTime=start_time.isoformat().replace("+00:00", "Z"),
        endTime=datetime(2024, 1, 5, 10, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
    )
)

experiment_request = ExperimentRequest.new(
    name=f"SDK-Example-{suffix}",
    description="Experiment created via SDK using legacy data format",
    product=product,
    process_unit=ProcessUnitCode.BR,  # Bioreactor
    variant_details=variant_details,
    data=openapi_data,  # pyright: ignore[reportArgumentType] - from_compat_data returns dict with Optional values for null handling, but API filters them out
    tags={"sdk-example": "true"},  # Tag for easy cleanup
)

# Submit the experiment
experiment = experiment_request.create(client)

# Verify by retrieving the data back
retrieved_data = experiment.get_data_compat()

# Resources created:
# - Variable: cqa_var.code
# - Experiment: experiment.display_name
# Clean up with: python examples/cleanup.py
