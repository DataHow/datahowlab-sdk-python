# Experiments

Experiments contain timeseries data for variables associated with a product.

## Creating Experiments

```python
from dhl_sdk import ExperimentData, TimeseriesData
from datetime import datetime

experiment = client.create_experiment(
    name="Experiment 001",
    product=product,
    variables=[variable1, variable2],
    data=ExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        timeseries={
            "VAR1": TimeseriesData(
                timestamps=[1735689600, 1735776000],
                values=[25.5, 26.3]
            ),
            "VAR2": TimeseriesData(
                timestamps=[1735689600, 1735776000],
                values=[100, 105]
            )
        }
    )
)
```

## Spectra Experiments

```python
from dhl_sdk import SpectraExperimentData, SpectraData

experiment = client.create_experiment(
    name="Spectra Experiment",
    product=product,
    variables=[spectra_variable],
    data=SpectraExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        spectra=SpectraData(
            wavelengths=[400, 500, 600],
            values=[[0.1, 0.2, 0.3], [0.15, 0.25, 0.35]]
        )
    )
)
```

## Retrieving Experiment Data

```python
data = client.get_experiment_data(experiment_id=experiment.id)
print(f"Variables: {len(data.variables)}")
print(f"Instances: {len(data.instances)}")
```

For complete details, see [Client API Reference](../api/client.md).
