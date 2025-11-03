"""Type definitions for DHL SDK v2

This module provides Pydantic models for type-safe data structures used throughout the SDK.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# ============================================================================
# Variable Types (Discriminated Union)
# ============================================================================


class VariableType(BaseModel):
    """Base class for variable types"""

    pass


class NumericVariable(VariableType):
    """Numeric variable with optional constraints"""

    kind: Literal["numeric"] = "numeric"
    min: float | None = None
    max: float | None = None
    default: float | None = None
    interpolation: Literal["linear", "discrete"] | None = None


class CategoricalVariable(VariableType):
    """Categorical variable with allowed categories"""

    kind: Literal["categorical"] = "categorical"
    categories: list[str] | None = None
    strict: bool = False
    default: str | None = None


class LogicalVariable(VariableType):
    """Boolean/logical variable"""

    kind: Literal["logical"] = "logical"
    default: bool | None = None


class FlowReference(BaseModel):
    """Reference to another variable in a flow variable"""

    measurement: str = Field(description="Variable code for measurement")
    concentration: str | None = Field(
        default=None, description="Variable code for concentration"
    )
    fraction: str | None = Field(default=None, description="Variable code for fraction")


class FlowVariable(VariableType):
    """Flow variable for modeling flows"""

    kind: Literal["flow"] = "flow"
    flow_type: Literal[
        "bolus", "conti", "mbolus", "mconti", "sampling", "bleed", "perfusion"
    ]
    references: list[FlowReference]
    step_size: int | None = Field(default=None, description="Step size in seconds")
    volume_variable: str | None = Field(
        default=None, description="Variable code for initial volume"
    )

    @field_validator("step_size")
    @classmethod
    def validate_step_size(cls, v, info):
        """Step size required for continuous flow types"""
        flow_type = info.data.get("flow_type")
        if flow_type in ["conti", "mconti", "bleed", "perfusion"] and not v:
            raise ValueError(f"step_size required for flow_type='{flow_type}'")
        return v


class SpectrumAxis(BaseModel):
    """Axis definition for spectrum variable"""

    dimension: int | None = None
    unit: str | None = None
    min: float | None = None
    max: float | None = None
    label: str | None = None


class SpectrumVariable(VariableType):
    """Spectrum/spectroscopy variable"""

    kind: Literal["spectrum"] = "spectrum"
    x_axis: SpectrumAxis | None = None
    y_axis: SpectrumAxis | None = None


# ============================================================================
# Experiment Data Structures
# ============================================================================


class TimeseriesData(BaseModel):
    """Time series data for a single variable"""

    timestamps: list[int] = Field(description="Unix timestamps (seconds since epoch)")
    values: list[float | str | bool]

    @field_validator("timestamps")
    @classmethod
    def validate_timestamps(cls, v):
        """Timestamps must be non-negative and sorted"""
        if not all(t >= 0 for t in v):
            raise ValueError("All timestamps must be non-negative")
        if v != sorted(v):
            raise ValueError("Timestamps must be sorted in ascending order")
        return v

    @field_validator("values")
    @classmethod
    def validate_values_length(cls, v, info):
        """Values must match timestamps length"""
        timestamps = info.data.get("timestamps", [])
        if len(v) != len(timestamps):
            raise ValueError(
                f"Values length ({len(v)}) must match timestamps length ({len(timestamps)})"
            )
        return v


class ExperimentData(BaseModel):
    """Data for a run or sample experiment"""

    variant: Literal["run", "samples"]
    start_time: datetime | None = Field(
        default=None, description="Required for 'run' variant"
    )
    end_time: datetime | None = Field(
        default=None, description="Required for 'run' variant"
    )
    timeseries: dict[str, TimeseriesData] = Field(
        description="Variable code -> timeseries data"
    )

    @model_validator(mode="after")
    def validate_run_variant_requirements(self) -> "ExperimentData":
        """Validate run variant has required time fields and timestamps in bounds"""
        if self.variant == "run":
            # Check required time fields
            if not self.start_time:
                raise ValueError("start_time required for variant='run'")
            if not self.end_time:
                raise ValueError("end_time required for variant='run'")

            # Validate timestamps are within bounds
            start_ts = int(self.start_time.timestamp())
            end_ts = int(self.end_time.timestamp())

            for var_code, ts_data in self.timeseries.items():
                for ts in ts_data.timestamps:
                    if not (start_ts <= ts <= end_ts):
                        raise ValueError(
                            f"Timestamp {ts} in variable '{var_code}' is outside "
                            f"experiment bounds [{start_ts}, {end_ts}]"
                        )

        return self


class SpectraData(BaseModel):
    """Spectra data structure"""

    timestamps: list[int] | None = Field(default=None, description="For run variant")
    sample_ids: list[str] | None = Field(
        default=None, description="For samples variant"
    )
    values: list[list[float]] = Field(
        description="2D array: [spectrum_index][wavelength_index]"
    )

    @field_validator("values")
    @classmethod
    def validate_spectra_dimensions(cls, v, info):
        """All spectra must have same dimension"""
        if not v:
            raise ValueError("At least one spectrum required")

        first_len = len(v[0])
        if not all(len(spectrum) == first_len for spectrum in v):
            raise ValueError("All spectra must have the same number of wavelengths")

        # Check that timestamps/sample_ids match number of spectra
        timestamps = info.data.get("timestamps")
        sample_ids = info.data.get("sample_ids")

        if timestamps and len(timestamps) != len(v):
            raise ValueError(
                f"Timestamps length ({len(timestamps)}) must match spectra count ({len(v)})"
            )

        if sample_ids and len(sample_ids) != len(v):
            raise ValueError(
                f"Sample IDs length ({len(sample_ids)}) must match spectra count ({len(v)})"
            )

        return v


class SpectraExperimentData(BaseModel):
    """Data for a spectra experiment"""

    variant: Literal["run", "samples"]
    start_time: datetime | None = None
    end_time: datetime | None = None
    spectra: SpectraData
    inputs: dict[str, list[float | str | bool]] | None = Field(
        default=None, description="Additional input variables: variable code -> values"
    )


# ============================================================================
# Prediction Input/Output Structures
# ============================================================================


class SpectraPredictionInput(BaseModel):
    """Input for spectra model predictions"""

    spectra: list[list[float]] = Field(description="2D array of spectra")
    inputs: dict[str, list[float | str]] | None = Field(
        default=None, description="Additional input variables"
    )


class PropagationPredictionInput(BaseModel):
    """Input for cultivation propagation model predictions"""

    timestamps: list[int | float]
    unit: Literal["s", "m", "h", "d"] = "s"
    inputs: dict[str, list[float]]
    confidence: float = Field(default=0.8, ge=0.01, le=0.99)
    starting_index: int = Field(default=0, ge=0)


class HistoricalPredictionInput(BaseModel):
    """Input for cultivation historical model predictions"""

    timestamps: list[int | float]
    steps: list[int]
    unit: Literal["s", "m", "h", "d"] = "s"
    inputs: dict[str, list[float]]
    confidence: float = Field(default=0.8, ge=0.01, le=0.99)

    @field_validator("steps")
    @classmethod
    def validate_steps_length(cls, v, info):
        """Steps must match timestamps length"""
        timestamps = info.data.get("timestamps", [])
        if len(v) != len(timestamps):
            raise ValueError(
                f"Steps length ({len(v)}) must match timestamps length ({len(timestamps)})"
            )
        return v


class PredictionOutput(BaseModel):
    """Structured prediction output"""

    outputs: dict[str, list[float]]
    confidence_intervals: dict[str, dict[str, list[float]]] | None = None
    metadata: dict[str, Any] | None = None


# ============================================================================
# Pagination
# ============================================================================


class PageInfo(BaseModel):
    """Pagination information"""

    total: int
    offset: int
    limit: int
    has_more: bool
