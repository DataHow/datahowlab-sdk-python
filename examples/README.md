# DataHowLab SDK Examples

This directory contains example scripts demonstrating how to use the DataHowLab
SDK.

## Examples

### Data Access

- `data_access.py` - Access experiment data using type-safe data format
- `data_access_compat.py` - Access experiment data using legacy data format

### Model Predictions

- `model_prediction.py` - Work with model predictions
- `model_prediction_compat.py` - Work with model predictions (legacy data
  format)

### Creating Resources

- `product_creation.py` - Create a new product
- `experiment_upload.py` - Create experiments with time-series data using
  type-safe data format
- `experiment_upload_compat.py` - Create experiments with time-series data using
  legacy data format

## Running Examples

All examples require the `DHL_API_KEY` environment variable to be set:

```bash
export DHL_API_KEY=your_api_key_here
python examples/product_creation.py
```

By default, examples connect to `https://example.datahowlab.ch/`. You can modify
the `base_url` parameter in each script to use a different environment.

## Important Notes for Experiment Upload

The experiment upload examples (`experiment_upload_openapi.py` and
`experiment_upload_compat.py`) demonstrate best practices:

1. **Fetch existing variables by code and group** - Uses
   `get_variables(code="...", group_code="...")` to find specific variables like
   Volume (Z), VCD (X), Glc (X), Gln (X), Temp (W), pH (W)
2. **Create new Y variable (CQA)** - Shows how to create a new output variable
   with proper min/max constraints
3. **Two data formats**:
   - **Type-safe data format** - Direct use of OpenAPI models
     (RawExperimentDataInputValue, NumericalTimeSeriesWithTimestamps, etc.)
   - **Legacy data format** - Simpler dict format
     `{code: {values: [...], timestamps: [...]}}` converted using
     `ExperimentRequest.from_compat_data()`
4. **Important constraints**:
   - Variable values must be within allowed ranges (if specified by min/max)
   - Timestamps must be within the experiment start/end time range
   - Feed/flow variables have interdependencies that require careful setup

## Cleaning Up Test Entities

When running examples, entities (products, variables, experiments) are created
with random suffixes to avoid naming collisions. All example entities are tagged
with `sdk-example: true` for easy cleanup.

### Automated Cleanup Script

The easiest way to clean up all test entities is to use the provided cleanup
script:

```bash
# Set your API key
export DHL_API_KEY=your_api_key_here

# Preview what would be deleted (dry run)
python examples/cleanup.py --dry-run

# Delete all entities tagged with sdk-example=true
python examples/cleanup.py

# Use a different environment
python examples/cleanup.py --base-url https://your-instance.datahowlab.ch/
```

The cleanup script will:

1. Find all experiments tagged with `sdk-example: true`
2. Find all products tagged with `sdk-example: true`
3. Find all variables tagged with `sdk-example: true`
4. Delete them in the correct order (experiments first, then products, then
   variables)
5. Display a summary of what was deleted

### Manual Cleanup Using the SDK

You can also delete entities programmatically using the SDK with tag filtering:

```python
from dhl_sdk import DataHowLabClient, APIKeyAuthentication

auth = APIKeyAuthentication()
client = DataHowLabClient(auth_key=auth, base_url="https://example.datahowlab.ch/")

# Find and delete experiments with sdk-example tag
for exp in client.get_experiments(tags={"sdk-example": "true"}):
    # Delete using API endpoint
    pass

# Find and delete products with sdk-example tag
for product in client.get_products(tags={"sdk-example": "true"}):
    # Delete using API endpoint
    pass

# Find and delete variables with sdk-example tag
for var in client.get_variables(tags={"sdk-example": "true"}):
    # Delete using API endpoint
    pass
```

### Manual Cleanup Using curl

You can also delete entities using the API directly. First, find entities by
tags:

```bash
# Set your API key
export DHL_API_KEY=your_api_key_here

# List experiments with sdk-example tag
curl -H "Api-Key: ${DHL_API_KEY}" \
  "https://example.datahowlab.ch/api/v1/experiments?tags[sdk-example]=true"

# List products with sdk-example tag
curl -H "Api-Key: ${DHL_API_KEY}" \
  "https://example.datahowlab.ch/api/v1/products?tags[sdk-example]=true"

# List variables with sdk-example tag
curl -H "Api-Key: ${DHL_API_KEY}" \
  "https://example.datahowlab.ch/api/v1/variables?tags[sdk-example]=true"
```

Then delete individual entities:

```bash
# Delete an experiment
curl -X DELETE -H "Api-Key: ${DHL_API_KEY}" \
  https://example.datahowlab.ch/api/v1/experiments/<experiment-id>

# Delete a product
curl -X DELETE -H "Api-Key: ${DHL_API_KEY}" \
  https://example.datahowlab.ch/api/v1/products/<product-id>

# Delete a variable
curl -X DELETE -H "Api-Key: ${DHL_API_KEY}" \
  https://example.datahowlab.ch/api/v1/variables/<variable-id>
```
