"""User-facing pydantic models"""

import uuid
from enum import Enum

from typing import Dict, List, Optional, Union
from pydantic import (
    BaseModel,
    Field,
    RootModel,
    field_validator,
    FiniteFloat,
)

from .helpers import json_path


InstanceValues = Union[list[Optional[FiniteFloat]], list[Optional[bool]], list[Optional[str]]]
""" Allowed types for the values of an Instance """


class OnlyId(BaseModel):
    """Model for objects with only ID (i.e. Variables, Experiments)"""

    id: uuid.UUID


# TODO: replace with API request
class ProcessFormatCode(Enum):
    """Process Format codes (temporary)

    * MAMMAL: Mammalian cell culture
    * MICRO: Microbial culture

    """

    MAMMAL = "MAMMAL"
    MICRO = "MICRO"


# TODO: replace with API request
class ProcessUnitCode(str, Enum):
    """Process Format codes (temporary)

    * BR: Cultivation/Bioreactor
    * SPC: Spectroscopy
    """

    BR = "BR"
    SPC = "SPC"


class Project(BaseModel):
    """DataHowLab Project"""

    id: uuid.UUID = Field(alias="id")
    name: str = Field(alias="name", description="Full display name")
    description: str = Field(alias="description", description="Extra verbose description")
    process_unit: ProcessUnitCode = Field(alias="processUnit", description="Process unit code")
    process_format: ProcessFormatCode = Field(alias="processFormat", description="Process format code")


class VariableVariant(str, Enum):
    """Enum for variable variants - data type per data point

    * flow: Numerical (float) data for feeds/flows
    * numeric: Numerical (float)/float data
    * categorical: Categorical (string) data
    * logical: Logical (boolean) data i.e. "true"/"false"
    * spectrum: Spectra (array of floats) data"""

    FLOW = "flow"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    LOGICAL = "logical"
    SPECTRUM = "spectrum"


class VariableInputType(str, Enum):
    """Variable Input Type

    * none: not an input type
    * scalar: single scalar value
    * initialTimeseries: initial timeseries values provided until first timestamp that is predicted
    * fullTimeseries: full timeseries data
    """

    NONE = "none"
    SCALAR = "scalar"
    INITIAL_TIMESERIES = "initialTimeseries"
    FULL_TIMESERIES = "fullTimeseries"


class VariableOutputType(str, Enum):
    """Variable Output Type

    * none: not an output variable
    * scalar: single scalar value
    * fullTimeseries: full timeseries data
    """

    NONE = "none"
    SCALAR = "scalar"
    FULL_TIMESERIES = "fullTimeseries"


class ModelType(str, Enum):
    """Model Type Enum

    * propagation: A propagation model predicts timeseries of measured variables from a recipe
    * historical: A historical model predicts final CQAs from complete timeseries of a finished experiment
    * combined: A combined model predicts both timeseries and CQAs from a recipe
    """

    PROPAGATION = "propagation"
    HISTORICAL = "historical"
    COMBINED = "combined"


class ModelVariable(BaseModel):
    """Model Input/Output Variable"""

    id: uuid.UUID = Field(alias="id")
    name: str = Field(alias="name", description="Full display name")
    code: str = Field(alias="code", description="Short name")
    description: str = Field(alias="description", description="Extra verbose description")
    measurement_unit: str = Field(alias="measurementUnit", description="Physical measurement unit")
    group: str = Field(alias="group", description="Variable group, e.g. X, W, Z, Y, Feeds")
    variant: VariableVariant = Field(
        alias="variant",
        description="Variable variant, determines data point type and extra meta-data",
    )
    input_type: VariableInputType = Field(
        alias="inputType",
        description="Indicates whether/how the variable is used as model input",
    )
    output_type: VariableOutputType = Field(
        alias="outputType",
        description="Indicates whether/what data will be predicted by the model",
    )
    disposition: str = Field(
        alias="disposition",
        description="Model-specific indicator of how a variable is used by the model",
    )

    @field_validator("group", mode="before")
    @classmethod
    def _extract_group_code(cls, value):
        """Validator that extracts code from group"""
        code = json_path(["code"], value)
        if code is None:
            raise ValueError("Invalid group: expected an object with 'code' key")
        return code


class ModelPredictionConfig(BaseModel):
    """Configuration settings for model prediction."""

    starting_timestamp: Optional[int] = Field(
        default=0,
        alias="startingTimestamp",
        description="Timestamp (in seconds) marking the starting point of the prediction",
    )
    model_confidence: Optional[int] = Field(
        default=80,
        alias="modelConfidence",
        ge=1,
        le=99,
        description="Value of confidence interval of the predictions, in percentage (between 1 and 99)",
    )


class PredictionPayload(BaseModel):
    """Request structure containing input data, timestamps, and optional configuration settings."""

    inputs: dict[uuid.UUID, InstanceValues] = Field(description="Dictionary of input values categorized by unique Variable IDs.")
    timestamps: list[int] = Field(
        description=(
            "List of timestamps, either in absolute unix timestamps "
            " (seconds since 1970-01-01 00:00:00 UTC)"
            "or in relative time in seconds (starting with 0)."
        ),
    )
    config: Optional[ModelPredictionConfig] = Field(
        default=None,
        description="Optional configuration parameters for controlling model predictions.",
    )


class ModelStatus(Enum):
    """Enum for Model Status

    * new: Training is pending
    * running: Training is progressing
    * failed: Training has failed
    * cancelled: Training was cancelled by the user
    * success: Training was successful
    """

    NEW = "new"
    RUNNING = "running"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUCCESS = "success"


class ModelReference(BaseModel):
    """Reference for model (Only for Combined Model)"""

    type: ModelType = Field(alias="type", description="Type of referenced model")
    model_id: uuid.UUID = Field(alias="modelId", description="UUID of referenced model")


class Model(BaseModel):
    """Predictive model from DataHowLab"""

    id: uuid.UUID = Field(alias="id")
    name: str = Field(alias="name", description="Full display name")
    description: str = Field(alias="description", description="Extra verbose description")
    status: ModelStatus = Field(alias="status", description="Status of model training")
    type: ModelType = Field(alias="type", description="Model type i.e. propagation, historical, etc")
    project_id: uuid.UUID = Field(alias="projectId", description="UUID of project hosting this model")
    dataset_id: uuid.UUID = Field(
        alias="datasetId",
        description="UUID of dataset with experiments used for model training/evaluation",
    )
    variant: str = Field(
        alias="variant",
        description="Specific model variant/version used e.g. Step-wise GP",
    )
    references: Optional[list[ModelReference]] = Field(default=None, description="Other models referenced by this model")
    step_size: int = Field(alias="stepSize", description="Tabularization step size [seconds]")


class NumericalTimeSeries(BaseModel):
    """Time series data for a given variable, with bounds."""

    values: List[Optional[float]] = Field(description="Predicted numerical time series values")
    upperBounds: Optional[List[Optional[float]]] = Field(
        description="Upper bounds of predicted numerical time series values, if supported by model"
    )
    lowerBounds: Optional[List[Optional[float]]] = Field(
        description="Lower bounds of predicted numerical time series values, if supported by model"
    )


class CategoricalTimeSeries(BaseModel):
    """Categorical Time series data for a given variable."""

    values: List[Optional[str]] = Field(description="Predictec categorical time series values")


class LogicalTimeSeries(BaseModel):
    """Logical Time series data for a given variable."""

    values: List[Optional[bool]] = Field(description="Predicted logical time series values")


class TimeSeriesPredictions(BaseModel):
    """One of numeric/categorical/logical."""

    numeric: Optional[NumericalTimeSeries] = Field(default=None, description="Predicted numerical time series")
    categorical: Optional[CategoricalTimeSeries] = Field(default=None, description="Predicted categorical time series")
    logical: Optional[LogicalTimeSeries] = Field(default=None, description="Predicted logical time series")


class NumericalScalar(BaseModel):
    """Represents a single scalar prediction with optional bounds."""

    value: Optional[float] = Field(default=None, description="Predicted numerical value")
    upperBound: Optional[float] = Field(
        default=None,
        description="Upper bound of predicted numerical value, if supported by model",
    )
    lowerBound: Optional[float] = Field(
        default=None,
        description="Lower bound of predicted numerical value, if supported by model",
    )


class CategoricalScalar(BaseModel):
    """Categorical scalar data for a given variable."""

    value: Optional[str] = Field(default=None, description="Predicted categorical value")


class LogicalScalar(BaseModel):
    """Logical Scalar data for a given variable."""

    value: Optional[bool] = Field(default=None, description="Predicted logical value")


class ScalarsPredictions(BaseModel):
    """One of numeric/categorical/logical."""

    numeric: Optional[NumericalScalar] = Field(default=None, description="Predicted numerical value")
    categorical: Optional[CategoricalScalar] = Field(default=None, description="Predicted categorical value")
    logical: Optional[LogicalScalar] = Field(default=None, description="Predicted logical value")


class Predictions(BaseModel):
    """One of timeseries/scalar."""

    timeseries: Optional[TimeSeriesPredictions] = None
    scalar: Optional[ScalarsPredictions] = None


class VariablePredictions(RootModel[Dict[uuid.UUID, Predictions]]):
    """Dictionary mapping variable UUIDs to predictions"""


class PredictionResponse(BaseModel):
    """Response for model predictions"""

    timestamps: Optional[List[int]] = Field(description="Shared timestamps for all time series predictions")
    predictions: VariablePredictions = Field(description="All predictions by variable UUID")
