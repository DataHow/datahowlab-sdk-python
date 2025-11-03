"""
Quick Start Example for DataHowLab SDK v2

This example demonstrates the most common operations:
1. Creating a product
2. Creating variables (numeric and categorical)
3. Creating an experiment with time-series data
4. Retrieving experiment data
5. Creating a recipe
6. Making predictions with a model
"""

from datetime import datetime

from dhl_sdk import (
    CategoricalVariable,
    DataHowLabClient,
    ExperimentData,
    NumericVariable,
    PropagationPredictionInput,
    TimeseriesData,
)

# =============================================================================
# 1. Initialize Client
# =============================================================================

client = DataHowLabClient(
    api_key="your-api-key",  # Or set DHL_API_KEY environment variable
    base_url="https://yourdomain.datahowlab.ch/",
)

print("✓ Client initialized")

# =============================================================================
# 2. Create Product
# =============================================================================

product = client.create_product(
    code="BATCH1",
    name="Production Batch 1",
    description="First production batch for cell culture",
    process_format="mammalian",
)

print(f"✓ Created product: {product.name} (ID: {product.id})")

# =============================================================================
# 3. Create Variables
# =============================================================================

# Numeric variable for temperature
temperature = client.create_variable(
    code="TEMP",
    name="Temperature",
    unit="°C",
    group="X Variables",
    type=NumericVariable(min=20.0, max=40.0, default=37.0, interpolation="linear"),
    description="Bioreactor temperature",
)

print(f"✓ Created variable: {temperature.name}")

# Categorical variable for process phase
phase = client.create_variable(
    code="PHASE",
    name="Process Phase",
    unit="n",
    group="Z Variables",
    type=CategoricalVariable(
        categories=["Init", "Growth", "Production", "Harvest"],
        strict=True,
        default="Init",
    ),
    description="Current process phase",
)

print(f"✓ Created variable: {phase.name}")

# Numeric variable for cell density
cell_density = client.create_variable(
    code="CELL_DENS",
    name="Cell Density",
    unit="cells/mL",
    group="Y Variables",
    type=NumericVariable(min=0, max=1e8, interpolation="linear"),
    description="Viable cell density",
)

print(f"✓ Created variable: {cell_density.name}")

# =============================================================================
# 4. Create Experiment with Time-Series Data
# =============================================================================

# Define time-series data
start_time = datetime(2025, 1, 1, 8, 0, 0)  # January 1, 2025, 8:00 AM
end_time = datetime(2025, 1, 15, 16, 0, 0)  # January 15, 2025, 4:00 PM

# Unix timestamps (seconds since epoch)
timestamps = [
    1735718400,  # Day 1
    1735804800,  # Day 2
    1735891200,  # Day 3
    1736064000,  # Day 5
    1736236800,  # Day 7
    1736409600,  # Day 9
    1736582400,  # Day 11
    1736755200,  # Day 13
    1736928000,  # Day 15
]

experiment = client.create_experiment(
    name="Batch Run 2025-001",
    description="Standard production run with CHO cells",
    product=product,
    variables=[temperature, phase, cell_density],
    data=ExperimentData(
        variant="run",
        start_time=start_time,
        end_time=end_time,
        timeseries={
            "TEMP": TimeseriesData(
                timestamps=timestamps,
                values=[37.0, 37.1, 37.0, 36.9, 37.1, 37.0, 37.2, 37.0, 37.1],
            ),
            "PHASE": TimeseriesData(
                timestamps=[timestamps[0], timestamps[2], timestamps[5], timestamps[8]],
                values=["Init", "Growth", "Production", "Harvest"],
            ),
            "CELL_DENS": TimeseriesData(
                timestamps=timestamps,
                values=[
                    5e5,
                    8e5,
                    1.5e6,
                    5e6,
                    1.2e7,
                    1.8e7,
                    2.0e7,
                    1.9e7,
                    1.7e7,
                ],
            ),
        },
    ),
)

print(f"✓ Created experiment: {experiment.name} (ID: {experiment.id})")

# =============================================================================
# 5. Retrieve Experiment Data
# =============================================================================

data = client.get_experiment_data(experiment)

print("\n✓ Retrieved experiment data:")
for var_code, var_data in data.items():
    num_points = len(var_data["timestamps"])
    print(f"  - {var_code}: {num_points} data points")

# =============================================================================
# 6. Create Recipe (Setpoint Profile)
# =============================================================================

recipe = client.create_recipe(
    name="Standard CHO Recipe",
    description="Standard temperature and feed profile for CHO cells",
    product=product,
    variables=[temperature],
    duration=1209600,  # 14 days in seconds
    data={
        "TEMP": TimeseriesData(
            timestamps=[0, 259200, 604800, 1209600],  # Day 0, 3, 7, 14
            values=[36.0, 37.0, 37.0, 36.5],
        )
    },
)

print(f"\n✓ Created recipe: {recipe.name} (ID: {recipe.id})")

# =============================================================================
# 7. Work with Projects and Models
# =============================================================================

# List projects
projects = client.list_projects(project_type="cultivation", process_format="mammalian")

if projects:
    project = projects[0]
    print(f"\n✓ Found project: {project.name}")

    # List models in project
    models = client.list_models(project, model_type="propagation")

    if models:
        model = models[0]
        print(f"✓ Found model: {model.name} (Status: {model.status})")

        # Check if model is ready for predictions
        if model.is_ready:
            # Make a prediction
            predictions = model.predict(
                client,
                PropagationPredictionInput(
                    timestamps=[0, 24, 48, 72, 96, 120, 144, 168],  # Hours
                    unit="h",
                    inputs={
                        "TEMP": [37.0],  # Initial value
                        "CELL_DENS": [5e5, 8e5, 1e6, 2e6, 5e6, 8e6, 1e7, 1.2e7],
                    },
                    confidence=0.8,  # 80% confidence interval
                ),
            )

            print("\n✓ Generated predictions:")
            for output_name, output_values in predictions.outputs.items():
                print(f"  - {output_name}: {len(output_values)} predictions")

            if predictions.confidence_intervals:
                print("  - Confidence intervals included")
        else:
            print(f"  ! Model not ready (status: {model.status})")
    else:
        print("  ! No models found in project")
else:
    print("\n! No projects found - skipping model prediction example")

# =============================================================================
# 8. Error Handling Example
# =============================================================================

print("\n" + "=" * 70)
print("Error Handling Examples")
print("=" * 70)

from dhl_sdk import EntityAlreadyExistsError, ValidationError  # noqa: E402

# Example 1: Validation error
try:
    invalid_product = client.create_product(code="", name="Invalid Product")
except ValidationError as e:
    print(f"\n✗ Validation Error: {e.message}")
    print(f"  Field: {e.field}")
    print(f"  Value: {e.value}")

# Example 2: Entity already exists
try:
    duplicate_product = client.create_product(
        code="BATCH1",  # Same code as before
        name="Duplicate Product",
    )
except EntityAlreadyExistsError as e:
    print(f"\n✗ Entity Already Exists: {e.message}")
    print(f"  Entity Type: {e.entity_type}")
    print(f"  Identifier: {e.entity_identifier}")

# =============================================================================
# Summary
# =============================================================================

print("\n" + "=" * 70)
print("Quick Start Complete!")
print("=" * 70)
print(
    """
Next steps:
1. Replace 'your-api-key' and base URL with your actual credentials
2. Adjust variable definitions to match your process
3. Use real timestamps from your production data
4. Explore the full API documentation in README.md
5. Check out the migration guide if upgrading from v1

For help: https://github.com/DataHow/datahowlab-sdk-python
"""
)
