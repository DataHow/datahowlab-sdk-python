# DataHowLab SDK v2.0 Examples

This directory contains examples demonstrating how to use the DataHowLab SDK v2.0.

## Available Examples

### 1. Jupyter Notebook Examples

#### **sdk_v2_comprehensive_examples.ipynb**
A comprehensive Jupyter notebook covering **all functions** available in the SDK v2.0. This is the best place to start for learning the SDK.

**Topics covered:**
- Client initialization and configuration
- Product operations (create, list, get)
- Variable operations (all types: numeric, categorical, logical, flow, spectrum)
- Experiment operations (create with time-series data, create with spectra data, retrieve data)
- Recipe operations (create setpoint profiles, list recipes)
- Project operations (list cultivation and spectroscopy projects)
- Model operations (list models, get model details, access model variables)
- Dataset operations (list datasets in projects)
- Prediction operations (spectroscopy, propagation, and historical models)
- Error handling (all error types)

**How to use:**
```bash
# Install Jupyter if you haven't already
pip install jupyter

# Start Jupyter notebook
jupyter notebook examples/sdk_v2_comprehensive_examples.ipynb
```

### 2. Python Script Examples

#### **quick_start.py**
A Python script demonstrating the most common SDK operations in a linear workflow.

**Topics covered:**
- Basic client setup
- Creating products and variables
- Creating experiments with time-series data
- Retrieving experiment data
- Creating recipes
- Working with projects and models
- Making predictions
- Error handling

**How to use:**
```bash
# Edit the script to add your API key and base URL
# Then run:
python examples/quick_start.py
```

## Prerequisites

Before running the examples, ensure you have:

1. **Python 3.9 or higher** installed
2. **DataHowLab SDK v2.0** installed:
   ```bash
   pip install dhl-sdk
   ```
3. **Valid API credentials**:
   - API key from your DataHowLab instance
   - Base URL of your DataHowLab instance

## Configuration

### Option 1: Environment Variable (Recommended)
```bash
export DHL_API_KEY="your-api-key"
```

### Option 2: Direct in Code
```python
from dhl_sdk import DataHowLabClient

client = DataHowLabClient(
    api_key="your-api-key",
    base_url="https://yourdomain.datahowlab.ch/"
)
```

## Quick Reference

### Client Initialization
```python
from dhl_sdk import DataHowLabClient

client = DataHowLabClient(
    api_key="your-key",
    base_url="https://yourdomain.datahowlab.ch/"
)
```

### Creating a Product
```python
product = client.create_product(
    code="PROD1",
    name="My Product",
    process_format="mammalian"
)
```

### Creating a Variable
```python
from dhl_sdk import NumericVariable

variable = client.create_variable(
    code="TEMP",
    name="Temperature",
    unit="°C",
    group="X Variables",
    type=NumericVariable(min=20.0, max=40.0)
)
```

### Creating an Experiment
```python
from dhl_sdk import ExperimentData, TimeseriesData
from datetime import datetime

experiment = client.create_experiment(
    name="My Experiment",
    product=product,
    variables=[variable],
    data=ExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        timeseries={
            "TEMP": TimeseriesData(
                timestamps=[1735689600, 1735776000],
                values=[37.0, 37.1]
            )
        }
    )
)
```

### Making Predictions
```python
from dhl_sdk import PropagationPredictionInput

# Get a model
projects = client.list_projects(project_type="cultivation")
models = client.list_models(projects[0])
model = models[0]

# Make predictions
predictions = model.predict(
    client,
    PropagationPredictionInput(
        timestamps=[0, 24, 48, 72],
        unit="h",
        inputs={"TEMP": [37.0]},
        confidence=0.8
    )
)

print(predictions.outputs)
```

## Support

- **Documentation**: See the main README.md in the repository root
- **Issues**: https://github.com/DataHow/datahowlab-sdk-python/issues
- **Migration Guide**: See MIGRATION.md for upgrading from v1.x to v2.0

## Variable Types Reference

The SDK supports the following variable types:

1. **NumericVariable** - For continuous numeric measurements
2. **CategoricalVariable** - For discrete categories
3. **LogicalVariable** - For boolean values
4. **FlowVariable** - For flows and feeds
5. **SpectrumVariable** - For spectroscopy data

See the comprehensive notebook for detailed examples of each type.

## Model Types

The SDK supports three types of models:

1. **Spectroscopy Models** - For predicting outputs from spectra
2. **Propagation Models** - For forward simulation of process dynamics
3. **Historical Models** - For predictions using historical data patterns

Each model type requires different input formats. See the comprehensive notebook for examples.
