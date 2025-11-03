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

## 📦 Installation

```bash
pip install datahowlab-sdk
```

Or with uv:

```bash
uv add datahowlab-sdk
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

## 📚 Next Steps

- [Installation Guide](getting-started/installation.md) - Detailed installation instructions
- [Quick Start Guide](getting-started/quick-start.md) - Complete working examples
- [User Guide](guide/client.md) - Comprehensive feature documentation
- [API Reference](api/client.md) - Complete API documentation
- [Migration Guide](migration.md) - Upgrading from v1 to v2

## 🎯 Key Features

### Type-Safe Data Structures

```python
from dhl_sdk import TimeseriesData, ValidationError

# Built-in validation
try:
    data = TimeseriesData(
        timestamps=[3, 1, 2],  # Not sorted!
        values=[1.0, 2.0, 3.0]
    )
except ValidationError as e:
    print(f"Error: {e.message}")  # "Timestamps must be sorted"
```

### Structured Error Handling

```python
from dhl_sdk import EntityNotFoundError, ValidationError

try:
    product = client.create_product(code="", name="Test")
except ValidationError as e:
    print(f"Validation failed on '{e.field}': {e.message}")
    print(f"Invalid value: {e.value}")
except EntityNotFoundError as e:
    print(f"Not found: {e.message}")
```

### Unified Prediction API

```python
from dhl_sdk import SpectraPredictionInput

# Works consistently across all model types
predictions = model.predict(
    client,
    SpectraPredictionInput(
        spectra=[[1.0, 2.0, 3.0]],
        inputs={"INPUT1": [42.0]}
    )
)
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/DataHow/datahowlab-sdk-python/blob/main/CONTRIBUTING.md) for guidelines.

## 📄 License

Apache License 2.0 - see [LICENSE](https://github.com/DataHow/datahowlab-sdk-python/blob/main/LICENSE) file for details.

## 💡 Support

- **Issues**: [GitHub Issues](https://github.com/DataHow/datahowlab-sdk-python/issues)
- **Email**: feedback@datahow.ch
- **Website**: [datahow.ch](https://datahow.ch/)

---

**Made with ❤️ by DataHow**
