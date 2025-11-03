# Data Validation Rules - SDK v2

This document describes all validation rules enforced by the DataHowLab SDK v2. All validations use Pydantic models and are checked at construction time, providing immediate feedback on invalid data.

## Table of Contents

- [Product Validation](#product-validation)
- [Variable Validation](#variable-validation)
- [Experiment Validation](#experiment-validation)
- [Recipe Validation](#recipe-validation)
- [Time-Series Data Validation](#time-series-data-validation)
- [Spectra Data Validation](#spectra-data-validation)
- [Prediction Input Validation](#prediction-input-validation)
- [Common Rules](#common-rules)

---

## Product Validation

### Code
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character
- **Max Length**: 10 characters
- **Format**: Automatically converted to uppercase
- **Whitespace**: Automatically stripped
- **Unique**: Yes (API enforced)

### Name
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character

### Description
- **Required**: No
- **Type**: String
- **Default**: Empty string

### Process Format
- **Required**: No
- **Type**: Literal["mammalian", "microbial"]
- **Default**: "mammalian"
- **Valid Values**:
  - `"mammalian"` - Mammalian cell culture processes
  - `"microbial"` - Microbial fermentation processes

---

## Variable Validation

### Code
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character
- **Max Length**: 15 characters
- **Format**: Automatically converted to uppercase
- **Whitespace**: Automatically stripped
- **Unique**: Yes (API enforced)

### Name
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character

### Unit
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character

### Group
- **Required**: Yes
- **Type**: String
- **Valid Values**: Any valid variable group from the API
- **Common Values**:
  - `"X Variables"` - Process inputs
  - `"Y Variables"` - Process outputs
  - `"Z Variables"` - Metadata/categorical variables
  - `"Flows"` - Flow rate variables

### Type
- **Required**: Yes
- **Type**: One of the variable type classes (discriminated union)
- **Valid Types**:
  - `NumericVariable`
  - `CategoricalVariable`
  - `LogicalVariable`
  - `FlowVariable`
  - `SpectrumVariable`

---

## Variable Type-Specific Validation

### NumericVariable

```python
NumericVariable(
    min: float | None = None,
    max: float | None = None,
    default: float | None = None,
    interpolation: Literal["linear", "previous", "next"] | None = None
)
```

- **min**: Optional minimum value
- **max**: Optional maximum value
- **default**: Optional default value
- **interpolation**: Optional interpolation method
  - `"linear"` - Linear interpolation between points
  - `"previous"` - Use previous value (step function)
  - `"next"` - Use next value (step function)

### CategoricalVariable

```python
CategoricalVariable(
    categories: list[str],
    strict: bool = False,
    default: str | None = None
)
```

- **categories**:
  - **Required**: Yes
  - **Type**: List of strings
  - **Min Length**: 1 category
  - **Uniqueness**: Categories should be unique

- **strict**:
  - **Type**: Boolean
  - **Default**: False
  - If True, only listed categories are allowed

- **default**:
  - **Type**: String or None
  - Must be one of the listed categories if provided

### LogicalVariable

```python
LogicalVariable(
    default: bool | None = None
)
```

- **default**: Optional default boolean value

### FlowVariable

```python
FlowVariable(
    flow_type: Literal["conti", "bolt"],
    references: list[FlowReference],
    step_size: int | None = None,
    volume_variable: str | None = None
)
```

- **flow_type**:
  - **Required**: Yes
  - **Valid Values**:
    - `"conti"` - Continuous flow
    - `"bolt"` - Bolus/discrete additions

- **references**:
  - **Required**: Yes
  - **Type**: List of FlowReference objects
  - **Min Length**: 1

- **step_size**:
  - **Required**: Yes for continuous flows (`flow_type="conti"`)
  - **Type**: Integer (seconds)
  - **Validation**: Must be positive if provided

- **volume_variable**:
  - **Type**: String (variable code) or None
  - References a volume variable for cumulative calculations

#### FlowReference

```python
FlowReference(
    measurement: str,
    concentration: str | None = None
)
```

- **measurement**: Variable code for flow rate measurement
- **concentration**: Optional variable code for concentration

### SpectrumVariable

```python
SpectrumVariable(
    x_axis: SpectrumAxis,
    y_axis: SpectrumAxis
)
```

- **x_axis**: Required SpectrumAxis configuration
- **y_axis**: Required SpectrumAxis configuration

#### SpectrumAxis

```python
SpectrumAxis(
    dimension: int | None = None,
    unit: str | None = None,
    min: float | None = None,
    max: float | None = None,
    label: str | None = None
)
```

- **dimension**: Number of points along this axis
- **unit**: Unit of measurement (e.g., "nm" for wavelength)
- **min**: Minimum value
- **max**: Maximum value
- **label**: Axis label

---

## Experiment Validation

### Name
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character

### Description
- **Required**: No
- **Type**: String
- **Default**: Empty string

### Product
- **Required**: Yes
- **Type**: Product object or product ID string

### Variables
- **Required**: Yes
- **Type**: List of Variable objects or variable ID strings

### Variant
- **Required**: Yes
- **Type**: Literal["run", "samples"]
- **Valid Values**:
  - `"run"` - Time-series experiment (requires start_time and end_time)
  - `"samples"` - Discrete samples (no time bounds required)

### Data
- **Required**: Yes
- **Type**: ExperimentData or SpectraExperimentData

---

## Time-Series Data Validation

### TimeseriesData

```python
TimeseriesData(
    timestamps: list[int],
    values: list[float | str | bool]
)
```

#### Timestamps
- **Required**: Yes
- **Type**: List of integers (Unix timestamps in seconds)
- **Validation Rules**:
  1. All timestamps must be positive (> 0)
  2. Timestamps must be sorted in ascending order
  3. Length must match values length

#### Values
- **Required**: Yes
- **Type**: List of float, string, or boolean
- **Validation Rules**:
  1. Length must match timestamps length
  2. Type should match variable type

### ExperimentData

```python
ExperimentData(
    variant: Literal["run", "samples"],
    timeseries: dict[str, TimeseriesData],
    start_time: datetime | None = None,
    end_time: datetime | None = None
)
```

- **variant**: Must be "run" or "samples"
- **timeseries**: Dictionary mapping variable codes to TimeseriesData
- **start_time**: Required if variant="run"
- **end_time**: Required if variant="run"

#### Additional Validation for variant="run":
- All timestamps in all timeseries must fall within [start_time, end_time]
- start_time must be before end_time
- Timestamps are compared as Unix timestamps (seconds)

---

## Spectra Data Validation

### SpectraData

```python
SpectraData(
    timestamps: list[int],
    values: list[list[float]]
)
```

#### Timestamps
- **Required**: Yes
- **Type**: List of integers
- **Validation**: Same as TimeseriesData timestamps
- **Length**: Must match number of spectra in values

#### Values
- **Required**: Yes
- **Type**: List of lists of floats (2D array)
- **Validation Rules**:
  1. All spectra must have the same number of wavelengths (dimension)
  2. Number of spectra must match number of timestamps
  3. All values must be numeric

### SpectraExperimentData

```python
SpectraExperimentData(
    variant: Literal["run", "samples"],
    spectra: SpectraData,
    inputs: dict[str, list[float | str | bool]] | None = None
)
```

- **variant**: Must be "run" or "samples"
- **spectra**: SpectraData object
- **inputs**: Optional dictionary of input variable values
  - Keys: Variable codes
  - Values: Lists of values (length must match number of spectra)

---

## Recipe Validation

### Name
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character

### Description
- **Required**: No
- **Type**: String
- **Default**: Empty string

### Product
- **Required**: Yes
- **Type**: Product object or product ID string

### Variables
- **Required**: Yes
- **Type**: List of Variable objects or variable ID strings

### Duration
- **Required**: No
- **Type**: Integer (seconds)
- **Validation**: Must be >= 0 if provided

### Data
- **Required**: Yes
- **Type**: Dictionary mapping variable codes to TimeseriesData

---

## Prediction Input Validation

### SpectraPredictionInput

```python
SpectraPredictionInput(
    spectra: list[list[float]],
    inputs: dict[str, list[float | str | bool]] | None = None
)
```

- **spectra**: List of spectra (2D array)
  - All spectra must have same dimension
- **inputs**: Optional input variables
  - Each list must have same length as number of spectra

### PropagationPredictionInput

```python
PropagationPredictionInput(
    timestamps: list[float | int],
    unit: Literal["s", "m", "h", "d"],
    inputs: dict[str, list[float | str | bool]],
    confidence: float | None = None,
    starting_index: int = 0
)
```

- **timestamps**: Time points for prediction
  - Must be sorted in ascending order
  - Must be positive

- **unit**: Time unit
  - `"s"` - seconds
  - `"m"` - minutes
  - `"h"` - hours
  - `"d"` - days

- **inputs**: Input variable values
  - Keys: Variable codes
  - Values: Lists (length 1 for initial values, or matching timestamps for time-varying)

- **confidence**: Confidence level (0.0-1.0)
- **starting_index**: Index to start prediction from (default 0)

### HistoricalPredictionInput

```python
HistoricalPredictionInput(
    timestamps: list[int],
    steps: list[int],
    unit: Literal["s", "m", "h", "d"],
    inputs: dict[str, list[float | str | bool]],
    confidence: float | None = None
)
```

- **timestamps**: Unix timestamps
  - Must be positive
  - Must be sorted

- **steps**: Step numbers
  - Must match timestamps length
  - Should be sequential

- **unit**: Time unit (same as PropagationPredictionInput)
- **inputs**: Input variable values
- **confidence**: Confidence level (0.0-1.0)

---

## Common Rules

### String Fields
- Empty strings after stripping whitespace are generally invalid for required fields
- Leading/trailing whitespace is automatically stripped for code fields
- Code fields are automatically converted to uppercase

### Numeric Fields
- Must be valid numbers (not NaN or Inf)
- Range constraints (min/max) are inclusive when specified

### Lists
- Cannot be empty when required
- All elements must be valid for their type
- Order matters for timestamps (must be sorted)

### Identifiers (IDs)
- Can accept either object references or string IDs
- SDK automatically extracts IDs from objects when needed

### Timestamps
- Always Unix timestamps (seconds since epoch) unless explicitly stated
- Must be positive integers
- Must be sorted in ascending order
- Must fall within experiment time bounds when applicable

---

## Error Messages

All validation errors are raised as `ValidationError` with structured information:

```python
try:
    data = TimeseriesData(timestamps=[3, 1, 2], values=[1.0, 2.0, 3.0])
except ValidationError as e:
    print(e.message)  # "Timestamps must be sorted"
    print(e.field)    # "timestamps"
    print(e.value)    # [3, 1, 2]
    print(e.details)  # {"field": "timestamps", "value": [3, 1, 2]}
```

---

## Best Practices

1. **Validate Early**: Create Pydantic models as soon as you have data
2. **Use Type Hints**: Let your IDE help catch errors before runtime
3. **Handle Exceptions**: Always catch and handle `ValidationError` appropriately
4. **Check Bounds**: Verify timestamps fall within experiment time bounds
5. **Match Dimensions**: Ensure all arrays have consistent dimensions
6. **Test Data**: Use small datasets first to verify structure

---

## Version History

- **v2.0.0** (2025-01-28): Complete rewrite with Pydantic validation
- Previous versions used separate validator classes (now removed)

For migration from v1, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).
