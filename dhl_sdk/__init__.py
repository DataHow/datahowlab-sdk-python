"""DataHowLab SDK v2.0

A simplified, type-safe SDK for interacting with the DataHowLab API.

Example usage:
    >>> from dhl_sdk import DataHowLabClient, NumericVariable, ExperimentData, TimeseriesData
    >>> from datetime import datetime
    >>>
    >>> # Initialize client
    >>> client = DataHowLabClient(api_key="your-key", base_url="https://...")
    >>>
    >>> # Create entities
    >>> product = client.create_product(code="PROD", name="My Product")
    >>> variable = client.create_variable(
    ...     code="VAR1", name="Variable 1", unit="ml",
    ...     group="X Variables", type=NumericVariable()
    ... )
    >>>
    >>> # Create experiment
    >>> experiment = client.create_experiment(
    ...     name="Exp1",
    ...     product=product,
    ...     variables=[variable],
    ...     data=ExperimentData(
    ...         variant="run",
    ...         start_time=datetime(2025, 1, 1),
    ...         end_time=datetime(2025, 1, 2),
    ...         timeseries={"VAR1": TimeseriesData(timestamps=[1735689600], values=[42.0])}
    ...     )
    ... )
    >>>
    >>> # List and retrieve
    >>> products = client.list_products(code="PROD")
    >>> experiments = client.list_experiments(product=product)
    >>>
    >>> # Model predictions
    >>> projects = client.list_projects(project_type="spectroscopy")
    >>> models = client.list_models(projects[0])
    >>> predictions = models[0].predict(client, SpectraPredictionInput(spectra=[[1.0, 2.0, 3.0]]))
"""

__version__ = "2.0.0"

__all__ = [
    "APIError",
    "AuthenticationError",
    "CategoricalVariable",
    "DHLError",
    "DataHowLabClient",
    "Dataset",
    "EntityAlreadyExistsError",
    "EntityNotFoundError",
    "Experiment",
    "ExperimentData",
    "FlowReference",
    "FlowVariable",
    "HistoricalPredictionInput",
    "LogicalVariable",
    "Model",
    "NumericVariable",
    "PermissionDeniedError",
    "PredictionError",
    "PredictionOutput",
    "Product",
    "Project",
    "PropagationPredictionInput",
    "RateLimitError",
    "Recipe",
    "ServerError",
    "SpectraData",
    "SpectraExperimentData",
    "SpectraPredictionInput",
    "SpectrumAxis",
    "SpectrumVariable",
    "TimeseriesData",
    "ValidationError",
    "Variable",
]

# Import from new modules
from dhl_sdk.client import DataHowLabClient
from dhl_sdk.errors import (
    APIError,
    AuthenticationError,
    DHLError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PermissionDeniedError,
    PredictionError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from dhl_sdk.models import (
    Dataset,
    Experiment,
    Model,
    Product,
    Project,
    Recipe,
    Variable,
)
from dhl_sdk.types import (
    CategoricalVariable,
    ExperimentData,
    FlowReference,
    FlowVariable,
    HistoricalPredictionInput,
    LogicalVariable,
    NumericVariable,
    PredictionOutput,
    PropagationPredictionInput,
    SpectraData,
    SpectraExperimentData,
    SpectraPredictionInput,
    SpectrumAxis,
    SpectrumVariable,
    TimeseriesData,
)
