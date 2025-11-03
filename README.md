# DataHowLab SDK v2

> **Simplified, Type-Safe Python SDK for DataHowLab**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/datahowlab-sdk.svg)](https://pypi.org/project/datahowlab-sdk/)

DataHowLab SDK provides a clean, intuitive interface for interacting with the DataHowLab API. Version 2.0 is a complete rewrite focused on simplicity, type safety, and developer experience.

## ✨ What's New in v2

- **50% Less Code**: Accomplish the same tasks with half the lines
- **Type-Safe**: Full Pydantic validation and type hints
- **Better Errors**: Structured exceptions with detailed context
- **No Reassignment**: Get IDs immediately on entity creation
- **Unified API**: Consistent patterns across all operations
- **One Client**: Single class for all operations
- **⏱️ Request Timeouts**: Configurable timeouts prevent hanging requests (default: 30s)
- **📄 Pagination Support**: Iterate over large datasets efficiently with `iter_all=True`
- **🔐 Enhanced Error Handling**: Specific exceptions for 401, 403, 429, 500+ errors

##  Prerequisites

- **Python 3.11+**
- **DataHowLab API Key**

## 📦 Installation

```bash
pip install datahowlab-sdk
```

Or with Poetry:

```bash
poetry add datahowlab-sdk
```

## 🚀 Quick Start

```python
from dhl_sdk import DataHowLabClient, NumericVariable, ExperimentData, TimeseriesData
from datetime import datetime

# Initialize client
client = DataHowLabClient(
    api_key="your-api-key",  # Or set DHL_API_KEY env var
    base_url="https://yourdomain.datahowlab.ch/"
)

# Create a product
product = client.create_product(
    code="PROD",
    name="My Product",
    description="Example product"
)

# Create a variable
variable = client.create_variable(
    code="VAR1",
    name="Temperature",
    unit="°C",
    group="X Variables",
    type=NumericVariable(min=0, max=100)
)

# Create an experiment
experiment = client.create_experiment(
    name="Experiment 1",
    product=product,
    variables=[variable],
    data=ExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        timeseries={
            "VAR1": TimeseriesData(
                timestamps=[1735689600, 1735776000],
                values=[25.5, 26.3]
            )
        }
    )
)

print(f"Created experiment: {experiment.name} (ID: {experiment.id})")
```

## 📚 Documentation

### Table of Contents

- [Client Initialization](#client-initialization)
- [Data Export](#data-export)
  - [Listing Entities](#listing-entities)
  - [Retrieving Experiment Data](#retrieving-experiment-data)
- [Data Import](#data-import)
  - [Creating Products](#creating-products)
  - [Creating Variables](#creating-variables)
  - [Creating Experiments](#creating-experiments)
- [Model Predictions](#model-predictions)
- [Error Handling](#error-handling)
- [Configuration](#configuration)

---

### Client Initialization

```python
from dhl_sdk import DataHowLabClient

# Option 1: Pass API key directly
client = DataHowLabClient(
    api_key="your-api-key",
    base_url="https://yourdomain.datahowlab.ch/",
    timeout=30.0  # Request timeout in seconds (default: 30.0)
)

# Option 2: Use environment variable
# Set DHL_API_KEY in your environment
client = DataHowLabClient(
    base_url="https://yourdomain.datahowlab.ch/",
    timeout=60.0  # Increase timeout for slow connections
)

# Option 3: Disable SSL verification (not recommended for production)
client = DataHowLabClient(
    api_key="your-key",
    base_url="https://...",
    verify_ssl=False
)

# Option 4: Use custom CA certificate
client = DataHowLabClient(
    api_key="your-key",
    base_url="https://...",
    verify_ssl="/path/to/certificate.pem"
)

# Option 5: Disable timeout (not recommended)
client = DataHowLabClient(
    api_key="your-key",
    base_url="https://...",
    timeout=None  # No timeout - requests can hang indefinitely
)
```

---

### Data Export

#### Listing Entities

All list operations return standard Python lists by default:

```python
# List first 100 products (default)
products = client.list_products(code="PROD", limit=100)

# Iterate over ALL products (automatically fetches pages as needed)
for product in client.list_products(iter_all=True):
    print(f"{product.code}: {product.name}")

# Iterate over products with filter
for product in client.list_products(code="PROD", iter_all=True):
    process_product(product)

# Note: iter_all=True returns an iterator for memory efficiency
# Use list() to convert to a list if needed:
all_products = list(client.list_products(iter_all=True))
product = products[0]  # Standard list access

# List variables
variables = client.list_variables(
    code="VAR1",
    group="X Variables",
    variable_type="numeric"
)

# List experiments
experiments = client.list_experiments(
    name="Experiment",
    product=product  # Can pass Product object or ID string
)

# List recipes
recipes = client.list_recipes(name="Recipe 1", product=product)

# List projects
projects = client.list_projects(
    name="My Project",
    project_type="spectroscopy",  # or "cultivation"
    process_format="mammalian"     # or "microbial"
)
```

#### Retrieving Experiment Data

```python
# Get experiment data
experiment = client.list_experiments(name="Exp1")[0]
data = client.get_experiment_data(experiment)

# Returns dict: {"VAR1": {"timestamps": [...], "values": [...]}, ...}
for var_code, var_data in data.items():
    print(f"{var_code}: {len(var_data['timestamps'])} data points")
```

---

### Data Import

#### Creating Products

```python
product = client.create_product(
    code="PROD",           # 1-10 characters, unique
    name="Product Name",
    description="Optional description",
    process_format="mammalian"  # or "microbial"
)
# product.id is immediately available
```

#### Creating Variables

**Numeric Variable:**
```python
from dhl_sdk import NumericVariable

variable = client.create_variable(
    code="TEMP",
    name="Temperature",
    unit="°C",
    group="X Variables",
    type=NumericVariable(
        min=0,
        max=100,
        default=25,
        interpolation="linear"
    ),
    description="Process temperature"
)
```

**Categorical Variable:**
```python
from dhl_sdk import CategoricalVariable

variable = client.create_variable(
    code="PHASE",
    name="Process Phase",
    unit="n",
    group="Z Variables",
    type=CategoricalVariable(
        categories=["Init", "Growth", "Production", "Harvest"],
        strict=True,
        default="Init"
    )
)
```

**Logical Variable:**
```python
from dhl_sdk import LogicalVariable

variable = client.create_variable(
    code="PUMP_ON",
    name="Pump Status",
    unit="bool",
    group="X Variables",
    type=LogicalVariable(default=False)
)
```

**Flow Variable:**
```python
from dhl_sdk import FlowVariable, FlowReference

# First create the measurement and concentration variables
measurement_var = client.create_variable(code="FLOW_RATE", ...)
concentration_var = client.create_variable(code="FEED_CONC", ...)

# Then create flow variable
flow_var = client.create_variable(
    code="FEED",
    name="Feed Flow",
    unit="L/h",
    group="Flows",
    type=FlowVariable(
        flow_type="conti",  # continuous flow
        references=[
            FlowReference(
                measurement=measurement_var.code,
                concentration=concentration_var.code
            )
        ],
        step_size=60,  # seconds
        volume_variable="VOLUME_VAR_CODE"
    )
)
```

**Get Available Variable Groups:**
```python
# Variable groups are fetched automatically
# Common groups: "X Variables", "Y Variables", "Z Variables", "Flows"
# The client validates group names automatically
```

#### Creating Experiments

**Standard Time-Series Experiment:**
```python
from dhl_sdk import ExperimentData, TimeseriesData
from datetime import datetime

experiment = client.create_experiment(
    name="Batch Run 001",
    description="First production batch",
    product=product,  # Or product ID string
    variables=[var1, var2],  # Or list of variable ID strings
    process_format="mammalian",
    data=ExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1, 8, 0, 0),
        end_time=datetime(2025, 1, 5, 16, 0, 0),
        timeseries={
            "TEMP": TimeseriesData(
                timestamps=[1735718400, 1735804800, 1735891200],
                values=[25.5, 26.0, 25.8]
            ),
            "PH": TimeseriesData(
                timestamps=[1735718400, 1735804800],
                values=[7.2, 7.1]
            )
        }
    )
)
```

**Spectra Experiment:**
```python
from dhl_sdk import SpectraExperimentData, SpectraData

experiment = client.create_experiment(
    name="Spectra Analysis 001",
    product=product,
    variables=[spectra_var, input_var1, input_var2],
    data=SpectraExperimentData(
        variant="run",
        spectra=SpectraData(
            timestamps=[1735718400, 1735804800, 1735891200],
            values=[
                [1.0, 1.1, 1.2, ..., 2.0],  # Spectrum 1
                [1.1, 1.2, 1.3, ..., 2.1],  # Spectrum 2
                [1.0, 1.1, 1.2, ..., 2.0],  # Spectrum 3
            ]
        ),
        inputs={
            "INPUT1": [42.0, 43.0, 44.0],
            "INPUT2": [100.0, 101.0, 102.0]
        }
    )
)
```

**Sample-Based Experiment:**
```python
experiment = client.create_experiment(
    name="Sample Analysis",
    product=product,
    variables=[var1, var2],
    data=ExperimentData(
        variant="samples",  # Not time-series
        timeseries={
            "VAR1": TimeseriesData(
                timestamps=[1, 2, 3],  # Sample IDs
                values=[10.5, 11.2, 10.8]
            )
        }
    )
)
```

**Important Notes:**
- Timestamps must be Unix timestamps (seconds since epoch)
- Timestamps must be sorted in ascending order
- For `variant="run"`, timestamps must fall within `start_time` and `end_time`
- All spectra must have the same number of wavelengths

---

### Model Predictions

**List Projects and Models:**
```python
# List projects
projects = client.list_projects(
    name="My Project",
    project_type="spectroscopy",
    process_format="mammalian"
)
project = projects[0]

# List models in a project
models = client.list_models(
    project=project,
    name="Production Model",
    model_type="propagation"  # For cultivation: "propagation" or "historical"
)
model = models[0]

# Check if model is ready
if model.is_ready:
    print(f"Model '{model.name}' is ready for predictions")
else:
    print(f"Model status: {model.status}")
```

**Spectra Model Predictions:**
```python
from dhl_sdk import SpectraPredictionInput

predictions = model.predict(
    client,
    SpectraPredictionInput(
        spectra=[
            [1.0, 1.1, 1.2, ..., 2.0],  # Spectrum 1
            [1.1, 1.2, 1.3, ..., 2.1],  # Spectrum 2
        ],
        inputs={
            "INPUT1": [42.0, 43.0]
        }
    )
)

# Access predictions
print(predictions.outputs)  # {"OUTPUT1": [value1, value2], "OUTPUT2": [...]}
print(predictions.confidence_intervals)  # Optional confidence intervals
print(predictions.metadata)  # Model metadata
```

**Cultivation Propagation Model:**
```python
from dhl_sdk import PropagationPredictionInput

predictions = model.predict(
    client,
    PropagationPredictionInput(
        timestamps=[0, 24, 48, 72, 96],  # Hours
        unit="h",  # "s", "m", "h", or "d"
        inputs={
            "INITIAL_CELL_DENSITY": [1.0e6],
            "FEED_RATE": [0, 2.0, 2.0, 2.0, 2.0]
        },
        confidence=0.8,  # 80% confidence interval
        starting_index=0
    )
)
```

**Cultivation Historical Model:**
```python
from dhl_sdk import HistoricalPredictionInput

predictions = model.predict(
    client,
    HistoricalPredictionInput(
        timestamps=[86400, 172800, 259200],  # Seconds
        steps=[0, 1, 2],  # Step progression
        unit="s",
        inputs={
            "VAR1": [42.0],
            "VAR2": [0.3],
            "VAR3": [0, 2, 3]
        },
        confidence=0.8
    )
)
```

---

### Error Handling

SDK v2 provides structured exceptions for better error handling:

```python
from dhl_sdk import (
    ValidationError,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    PredictionError,
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
    ServerError
)

try:
    product = client.create_product(code="", name="Test")

except ValidationError as e:
    # Field-level validation errors
    print(f"Validation failed on '{e.field}': {e.message}")
    print(f"Invalid value: {e.value}")
    # e.details contains additional context

except EntityAlreadyExistsError as e:
    # Entity with same code/name already exists
    print(f"Already exists: {e.message}")
    print(f"Entity type: {e.entity_type}")

except EntityNotFoundError as e:
    # Referenced entity doesn't exist
    print(f"Not found: {e.message}")
    print(f"Entity type: {e.entity_type}")

except AuthenticationError as e:
    # HTTP 401 - Invalid API key or unauthorized
    print(f"Authentication failed: {e.message}")

except PermissionDeniedError as e:
    # HTTP 403 - Insufficient permissions
    print(f"Permission denied: {e.message}")
    print(f"Resource: {e.resource}")

except RateLimitError as e:
    # HTTP 429 - Rate limit exceeded
    print(f"Rate limited: {e.message}")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")

except ServerError as e:
    # HTTP 500+ - Server-side errors
    print(f"Server error (HTTP {e.status_code}): {e.message}")
    print("The API is experiencing issues. Please try again later.")

except APIError as e:
    # General API error
    print(f"API error (HTTP {e.status_code}): {e.message}")
    print(f"Response: {e.response_body}")

except PredictionError as e:
    # Model prediction failed
    print(f"Prediction failed: {e.message}")
    print(f"Details: {e.details}")
```

#### Exception Hierarchy

All SDK exceptions inherit from `DHLError`:

```
DHLError (base exception)
├── ValidationError         # Input validation failure
├── EntityNotFoundError     # HTTP 404
├── EntityAlreadyExistsError # HTTP 409
├── AuthenticationError     # HTTP 401
├── PermissionDeniedError   # HTTP 403
├── RateLimitError          # HTTP 429
├── ServerError             # HTTP 500, 502, 503, 504
├── PredictionError         # Model prediction failure
└── APIError                # General API/network errors
```

---

### Configuration

#### SSL/TLS Certificates

**Option 1: Using truststore (Recommended)**

For environments with custom CA certificates trusted by the system:

```python
import truststore
truststore.inject_into_ssl()

from dhl_sdk import DataHowLabClient

client = DataHowLabClient(api_key="...", base_url="...")
```

**Option 2: Custom Certificate**

Point to a specific certificate file:

```python
client = DataHowLabClient(
    api_key="...",
    base_url="...",
    verify_ssl="/path/to/certificate.pem"
)
```

**Option 3: Disable Verification (Not Recommended)**

```python
client = DataHowLabClient(
    api_key="...",
    base_url="...",
    verify_ssl=False
)
```

⚠️ **Warning:** Disabling SSL verification exposes you to security risks. Only use in trusted networks.

---

## 🏗️ Architecture & Design

### Clean Service Architecture

The SDK follows a clean, modular architecture with separation of concerns:

**Core Components:**
- **`DataHowLabClient`**: Main entry point for all API operations
- **`FileService`**: Handles file uploads/downloads (CSV, JSON)
- **`DataFormatService`**: Manages data formatting and parsing
- **`PageIterator`**: Memory-efficient pagination for large datasets

**Design Principles:**
- **Single Responsibility**: Each service class has one clear purpose
- **Dependency Injection**: Services are injected into the client for testability
- **Type Safety**: Full Pydantic validation with discriminated unions
- **Backward Compatibility**: v2 API maintains list-based defaults while adding iterator support

### Lightweight Dependencies

The v2 SDK core has minimal dependencies:
- **Pydantic 2.x**: For data validation and parsing
- **requests**: For HTTP operations

---

## 🔄 Migrating from v1

If you're upgrading from SDK v0.x (v1), see our comprehensive [Migration Guide](MIGRATION_GUIDE.md).

**Key Changes:**
- Single client class (no separate `APIKeyAuthentication`)
- Direct creation methods (`client.create_product()` vs `Product.new()` + `client.create()`)
- Type-safe data structures (`ExperimentData` vs plain dicts)
- Unified prediction API across all model types
- Structured error handling

---

## 📖 Additional Resources

- **[Migration Guide](MIGRATION_GUIDE.md)** - Detailed v1 → v2 migration instructions
- **[Changelog](CHANGELOG.md)** - Complete list of changes
- **[Examples Notebook](examples.ipynb)** - Interactive examples
- **[Validation Rules](validations.md)** - Data validation documentation
- **[GitHub Issues](https://github.com/DataHow/datahowlab-sdk-python/issues)** - Report bugs or request features

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

---

## 💡 Support

- **Issues**: [GitHub Issues](https://github.com/DataHow/datahowlab-sdk-python/issues)
- **Email**: feedback@datahow.ch
- **Website**: [datahow.ch](https://datahow.ch/)

---

**Made with ❤️ by DataHow**
