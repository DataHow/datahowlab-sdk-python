# Variables

Variables define the measurements and parameters tracked in experiments.

## Variable Types

### Numeric Variables

```python
from dhl_sdk import NumericVariable

variable = client.create_variable(
    code="TEMP",
    name="Temperature",
    unit="°C",
    group="Process Variables",
    type=NumericVariable(min=0, max=100)
)
```

### Categorical Variables

```python
from dhl_sdk import CategoricalVariable

variable = client.create_variable(
    code="STATUS",
    name="Status",
    group="Quality",
    type=CategoricalVariable(categories=["Pass", "Fail"])
)
```

### Spectra Variables

```python
from dhl_sdk import SpectraVariable

variable = client.create_variable(
    code="SPECTRA",
    name="NIR Spectra",
    unit="nm",
    group="Spectra",
    type=SpectraVariable(size=1000)
)
```

## Listing Variables

```python
# List all variables
variables = client.list_variables()

# Filter by code or group
variables = client.list_variables(code="TEMP")
variables = client.list_variables(group="Process Variables")
```

For more details, see [Types API Reference](../api/types.md).
