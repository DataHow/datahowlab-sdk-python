# Migration Guide: v1 → v2

This guide helps you migrate from DataHowLab SDK v1 (0.x) to v2 (2.0+).

## Table of Contents
- [Overview](#overview)
- [Breaking Changes Summary](#breaking-changes-summary)
- [Step-by-Step Migration](#step-by-step-migration)
  - [1. Client Initialization](#1-client-initialization)
  - [2. Creating Products](#2-creating-products)
  - [3. Creating Variables](#3-creating-variables)
  - [4. Creating Experiments](#4-creating-experiments)
  - [5. Listing Entities](#5-listing-entities)
  - [6. Model Predictions](#6-model-predictions)
  - [7. Error Handling](#7-error-handling)
- [Quick Reference](#quick-reference)

---

## Overview

SDK v2 is a complete rewrite focused on:
- **Simplicity**: Fewer steps, clearer APIs
- **Type Safety**: Full Pydantic validation and type hints
- **Better Errors**: Structured exceptions with details
- **Less Code**: 50% reduction in typical usage

**Migration effort**: ~2-4 hours for typical applications

> **⚠️ Important**: Starting with v2.0.0, the SDK no longer supports legacy v1 **SDK code patterns** (`_legacy/` directory removed). This means old code like `Product.new()` → `client.create()` will not work. However, the **backend API endpoints remain unchanged** at `/api/db/v2/` - this is purely a Python SDK architecture change. If you need to maintain v1 SDK code patterns, pin your installation to `datahowlab-sdk<2.0.0`. For new projects and migrations, use v2.0.0+ for the best experience.

---

## Breaking Changes Summary

| Area | v1 | v2 |
|------|----|----|
| **Client Init** | `APIKeyAuthentication()` + `DataHowLabClient(auth_key, ...)` | `DataHowLabClient(api_key, ...)` |
| **Entity Creation** | `Entity.new(...)`  → `client.create(entity)` | `client.create_entity(...)` (direct) |
| **Variable Types** | `VariableNumeric()`, `VariableCategorical()` as separate classes | `NumericVariable()`, `CategoricalVariable()` in `type` parameter |
| **Experiment Data** | Plain dict | `ExperimentData` or `SpectraExperimentData` Pydantic models |
| **Predictions** | Different `predict()` signatures per model | Unified `predict()` with typed input classes |
| **Error Handling** | Generic exceptions | Structured exceptions (`ValidationError`, `EntityNotFoundError`, etc.) |
| **Imports** | `from dhl_sdk import ...` mixed | Clean, organized imports |

---

## Step-by-Step Migration

### 1. Client Initialization

#### v1 (Before)
```python
from dhl_sdk import APIKeyAuthentication, DataHowLabClient

auth = APIKeyAuthentication()  # Or APIKeyAuthentication("key")
client = DataHowLabClient(auth_key=auth, base_url="https://...")
```

#### v2 (After)
```python
from dhl_sdk import DataHowLabClient

client = DataHowLabClient(api_key="your-key", base_url="https://...")
# Or let it read from DHL_API_KEY env var:
client = DataHowLabClient(base_url="https://...")
```

**Changes:**
- No separate `APIKeyAuthentication` class
- Pass `api_key` directly to client
- Still reads from `DHL_API_KEY` env var if not provided

---

### 2. Creating Products

#### v1 (Before)
```python
from dhl_sdk import Product

product = Product.new(code="PROD", name="My Product", description="...")
product = client.create(product)  # Must reassign to get ID!
print(product.id)  # Now has ID
```

#### v2 (After)
```python
product = client.create_product(
    code="PROD",
    name="My Product",
    description="..."
)
print(product.id)  # ID returned immediately
```

**Changes:**
- Direct creation method on client
- No `.new()` + `.create()` pattern
- No need to reassign
- ID returned immediately

---

### 3. Creating Variables

#### v1 (Before)
```python
from dhl_sdk import Variable, VariableNumeric, VariableCategorical

# Numeric variable
numeric_var = Variable.new(
    code="VAR1",
    name="Variable 1",
    measurement_unit="ml",
    variable_group="X Variables",
    variable_type=VariableNumeric(min=0, max=100),
    description="..."
)
numeric_var = client.create(numeric_var)

# Categorical variable
cat_var = Variable.new(
    code="VAR2",
    name="Variable 2",
    measurement_unit="n",
    variable_group="Z Variables",
    variable_type=VariableCategorical(categories=["A", "B", "C"]),
)
cat_var = client.create(cat_var)
```

#### v2 (After)
```python
from dhl_sdk import NumericVariable, CategoricalVariable

# Numeric variable
numeric_var = client.create_variable(
    code="VAR1",
    name="Variable 1",
    unit="ml",
    group="X Variables",
    type=NumericVariable(min=0, max=100),
    description="..."
)

# Categorical variable
cat_var = client.create_variable(
    code="VAR2",
    name="Variable 2",
    unit="n",
    group="Z Variables",
    type=CategoricalVariable(categories=["A", "B", "C"])
)
```

**Changes:**
- Import types directly: `NumericVariable`, `CategoricalVariable`, etc.
- Use `unit` instead of `measurement_unit`
- Use `group` instead of `variable_group`
- Use `type` parameter instead of `variable_type`
- Direct creation on client

---

### 4. Creating Experiments

#### v1 (Before)
```python
from dhl_sdk import Experiment

experiment = Experiment.new(
    name="Exp1",
    description="Test experiment",
    product=product,
    variables=[var1, var2],
    data_type="run",
    variant="run",
    data={
        "VAR1": {
            "timestamps": [1600674350, 1600760750],
            "values": [5.1, 3.5]
        },
        "VAR2": {
            "timestamps": [1600674350],
            "values": ["A"]
        }
    },
    start_time="2020-09-21T08:45:50Z",
    end_time="2020-10-05T08:45:50Z"
)
experiment = client.create(experiment)
```

#### v2 (After)
```python
from dhl_sdk import ExperimentData, TimeseriesData
from datetime import datetime

experiment = client.create_experiment(
    name="Exp1",
    description="Test experiment",
    product=product,  # Or just product ID string
    variables=[var1, var2],  # Or just variable ID strings
    data=ExperimentData(
        variant="run",
        start_time=datetime(2020, 9, 21, 8, 45, 50),
        end_time=datetime(2020, 10, 5, 8, 45, 50),
        timeseries={
            "VAR1": TimeseriesData(
                timestamps=[1600674350, 1600760750],
                values=[5.1, 3.5]
            ),
            "VAR2": TimeseriesData(
                timestamps=[1600674350],
                values=["A"]
            )
        }
    )
)
```

**Changes:**
- Wrap data in `ExperimentData` Pydantic model
- Use `TimeseriesData` for each variable
- Use `datetime` objects instead of ISO strings
- No separate `data_type` parameter
- Direct creation on client
- Can pass Product/Variable objects OR just ID strings

**For Spectra Experiments:**

```python
from dhl_sdk import SpectraExperimentData, SpectraData

experiment = client.create_experiment(
    name="Spectra Exp",
    product=product,
    variables=[spectra_var, input_var],
    data=SpectraExperimentData(
        variant="run",
        spectra=SpectraData(
            timestamps=[1, 2, 3],
            values=[[1.0, 2.0, 3.0], [1.1, 2.1, 3.1], [1.2, 2.2, 3.2]]
        ),
        inputs={"INPUT1": [42, 43, 44]}
    )
)
```

---

### 5. Listing Entities

#### v1 (Before)
```python
# Returns Result[T] iterator
products = client.get_products(code="PROD")
product = next(products)  # Must use next()

experiments = client.get_experiments(name="exp", product=product)
exp = next(experiments)
```

#### v2 (After)
```python
# Returns list directly
products = client.list_products(code="PROD")
product = products[0]  # Standard list access

experiments = client.list_experiments(name="exp", product=product)
exp = experiments[0]
```

**Changes:**
- `get_*` renamed to `list_*`
- Returns list instead of iterator
- Standard list operations work
- No need for `next()`

---

### 6. Model Predictions

#### v1 (Before - Spectra)
```python
from dhl_sdk import Project

projects = client.get_projects(name="...", project_type="spectroscopy")
project = next(projects)

models = project.get_models(name="Test model")
model = next(models)

# Different signature per model type!
predictions = model.predict(
    spectra=[[1.0, 2.0, 3.0]],
    inputs={"INPUT1": [42]}
)
```

#### v2 (After - Spectra)
```python
from dhl_sdk import SpectraPredictionInput

projects = client.list_projects(name="...", project_type="spectroscopy")
project = projects[0]

models = client.list_models(project, name="Test model")
model = models[0]

# Unified interface with typed input!
predictions = model.predict(
    client,
    SpectraPredictionInput(
        spectra=[[1.0, 2.0, 3.0]],
        inputs={"INPUT1": [42]}
    )
)
```

#### v1 (Before - Cultivation Propagation)
```python
model = next(project.get_models(name="...", model_type="propagation"))

predictions = model.predict(
    timestamps=[1, 2, 3, 4],
    inputs={"VAR1": [42], "VAR2": [0.3]},
    timestamps_unit="d",
    config=PredictionConfig(model_confidence=80)
)
```

#### v2 (After - Cultivation Propagation)
```python
from dhl_sdk import PropagationPredictionInput

models = client.list_models(project, model_type="propagation")
model = models[0]

predictions = model.predict(
    client,
    PropagationPredictionInput(
        timestamps=[1, 2, 3, 4],
        unit="d",
        inputs={"VAR1": [42], "VAR2": [0.3]},
        confidence=0.8
    )
)
```

**Changes:**
- All models use same `predict()` method
- Pass `client` as first argument
- Wrap inputs in typed classes
- Consistent output format
- `list_models()` instead of `project.get_models()`

---

### 7. Error Handling

#### v1 (Before)
```python
try:
    product = Product.new(code="", name="Test")
    client.create(product)
except Exception as e:
    print(f"Error: {e}")  # Generic message
```

#### v2 (After)
```python
from dhl_sdk import ValidationError, EntityAlreadyExistsError, APIError

try:
    product = client.create_product(code="", name="Test")
except ValidationError as e:
    print(f"Validation failed on field '{e.field}': {e.message}")
    print(f"Invalid value: {e.value}")
except EntityAlreadyExistsError as e:
    print(f"Entity already exists: {e.message}")
    print(f"Details: {e.details}")
except APIError as e:
    print(f"API error (status {e.status_code}): {e.message}")
```

**Changes:**
- Specific exception types
- Structured error information
- Field-level validation details
- HTTP status codes included
- Programmatic error handling

---

## Quick Reference

### Import Changes

```python
# v1
from dhl_sdk import (
    APIKeyAuthentication,
    DataHowLabClient,
    Product,
    Variable,
    VariableNumeric,
    VariableCategorical,
    Experiment,
)

# v2
from dhl_sdk import (
    DataHowLabClient,
    NumericVariable,
    CategoricalVariable,
    ExperimentData,
    TimeseriesData,
    SpectraPredictionInput,
    ValidationError,
)
```

### Common Operations

| Operation | v1 | v2 |
|-----------|----|----|
| **Create Product** | `Product.new(...)`<br/>`client.create(product)` | `client.create_product(...)` |
| **Create Variable** | `Variable.new(..., variable_type=VariableNumeric())`<br/>`client.create(var)` | `client.create_variable(..., type=NumericVariable())` |
| **Create Experiment** | `Experiment.new(..., data={...})`<br/>`client.create(exp)` | `client.create_experiment(..., data=ExperimentData(...))` |
| **List Products** | `next(client.get_products())` | `client.list_products()[0]` |
| **List Experiments** | `next(client.get_experiments())` | `client.list_experiments()[0]` |
| **Get Experiment Data** | `experiment.get_data(client)` | `client.get_experiment_data(experiment)` |
| **Model Prediction** | `model.predict(spectra=[...])` | `model.predict(client, SpectraPredictionInput(spectra=[...]))` |

---

## Tips for Smooth Migration

1. **Start with imports**: Update all imports first
2. **Fix client initialization**: Change authentication pattern
3. **Update entity creation**: Replace `.new()` + `.create()` with direct methods
4. **Wrap data structures**: Add Pydantic models around data
5. **Update error handling**: Catch specific exception types
6. **Test incrementally**: Migrate one module at a time
7. **Use type hints**: Let your IDE guide you with autocomplete

---

## Need Help?

- Check the updated [README.md](README.md) for examples
- Review [examples.ipynb](examples.ipynb) for complete workflows
- See [CHANGELOG.md](CHANGELOG.md) for all breaking changes
- Open an issue on GitHub if you're stuck

**Happy migrating! 🚀**
