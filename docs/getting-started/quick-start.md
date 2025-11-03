# Quick Start

This guide will help you get started with the DataHowLab SDK in minutes.

## Prerequisites

- [Installed the SDK](installation.md)
- DataHowLab API key
- DataHowLab instance URL

## Initialize the Client

```python
from dhl_sdk import DataHowLabClient

client = DataHowLabClient(
    api_key="your-api-key",  # Or set DHL_API_KEY environment variable
    base_url="https://yourdomain.datahowlab.ch/"
)
```

## Basic Operations

### Create a Product

```python
product = client.create_product(
    code="PROD001",
    name="My Product",
    description="Example product"
)
print(f"Created product: {product.id}")
```

### Create a Variable

```python
from dhl_sdk import NumericVariable

variable = client.create_variable(
    code="TEMP",
    name="Temperature",
    unit="°C",
    group="Process Variables",
    type=NumericVariable(min=0, max=100)
)
print(f"Created variable: {variable.id}")
```

### Create an Experiment

```python
from dhl_sdk import ExperimentData, TimeseriesData
from datetime import datetime

experiment = client.create_experiment(
    name="Experiment 001",
    product=product,
    variables=[variable],
    data=ExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        timeseries={
            "TEMP": TimeseriesData(
                timestamps=[1735689600, 1735776000],
                values=[25.5, 26.3]
            )
        }
    )
)
print(f"Created experiment: {experiment.id}")
```

### List Entities

```python
# List all products
products = client.list_products()
for product in products:
    print(f"{product.code}: {product.name}")

# Use pagination for large datasets
all_experiments = list(client.list_experiments(iter_all=True))
print(f"Total experiments: {len(all_experiments)}")
```

### Get Experiment Data

```python
# Retrieve data for an experiment
data = client.get_experiment_data(experiment.id)
print(f"Variables: {len(data.variables)}")
print(f"Instances: {len(data.instances)}")
```

## Error Handling

```python
from dhl_sdk import EntityNotFoundError, ValidationError

try:
    product = client.get_product("nonexistent-id")
except EntityNotFoundError as e:
    print(f"Product not found: {e.entity_id}")
except ValidationError as e:
    print(f"Validation error: {e.validation_errors}")
```

## Next Steps

- Explore the [User Guide](../guide/client.md) for detailed information
- Check the [API Reference](../api/client.md) for all available methods
- Review [Validation Rules](../validations.md) to understand data constraints
