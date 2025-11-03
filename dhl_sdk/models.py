"""Entity models for DHL SDK v2

Simplified Pydantic models representing DHL entities.
All validation is built into the models using Pydantic validators.
"""

from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import BaseModel, Field, field_validator

from dhl_sdk.types import (
    CategoricalVariable,
    FlowVariable,
    HistoricalPredictionInput,
    LogicalVariable,
    NumericVariable,
    PredictionOutput,
    PropagationPredictionInput,
    SpectraPredictionInput,
    SpectrumVariable,
)

if TYPE_CHECKING:
    from dhl_sdk.client import DataHowLabClient


# ============================================================================
# Core Entities
# ============================================================================


class Product(BaseModel):
    """Product entity

    Attributes:
        id: Unique identifier (set by server)
        code: Product code (1-10 characters, unique)
        name: Product name
        description: Optional description
        process_format: Process format type
    """

    id: str | None = None
    code: str = Field(min_length=1, max_length=10)
    name: str
    description: str = ""
    process_format: Literal["mammalian", "microbial"] = "mammalian"

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Normalize and validate code"""
        v = v.strip()
        if not v:
            raise ValueError("Code cannot be empty")
        return v.upper()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty"""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class Variable(BaseModel):
    """Variable entity

    Attributes:
        id: Unique identifier (set by server)
        code: Variable code (unique, max 20 characters)
        name: Variable name
        unit: Measurement unit
        group: Variable group (e.g., "X Variables", "Z Variables")
        type: Variable type (discriminated union)
        description: Optional description
    """

    id: str | None = None
    code: str = Field(min_length=1, max_length=10)
    name: str
    unit: str
    group: str
    type: Annotated[
        NumericVariable
        | CategoricalVariable
        | LogicalVariable
        | FlowVariable
        | SpectrumVariable,
        Field(discriminator="kind"),
    ]
    description: str = ""

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Normalize and validate code"""
        v = v.strip()
        if not v:
            raise ValueError("Code cannot be empty")
        return v.upper()

    @field_validator("name", "unit", "group")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate required fields are not empty"""
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v


class Experiment(BaseModel):
    """Experiment entity

    Attributes:
        id: Unique identifier (set by server)
        name: Experiment name
        description: Optional description
        product: Associated product (can be Product object or product ID string)
        process_format: Process format
        variant: Experiment variant (run for time-series, samples for discrete samples)
        variables: List of variables (can be Variable objects or variable ID strings)
    """

    id: str | None = None
    name: str
    description: str = ""
    product: Product | str  # Product object or ID
    process_format: Literal["mammalian", "microbial"] = "mammalian"
    variant: Literal["run", "samples"] = "run"
    variables: list[Variable | str] = []  # Variable objects or IDs

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty"""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class Recipe(BaseModel):
    """Recipe entity

    Attributes:
        id: Unique identifier (set by server)
        name: Recipe name
        description: Optional description
        product: Associated product
        duration: Optional duration in seconds (must be non-negative)
        variables: List of variables
    """

    id: str | None = None
    name: str
    description: str = ""
    product: Product | str
    duration: int | None = Field(default=None, ge=0)
    variables: list[Variable | str] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty"""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


# ============================================================================
# Project and Model Entities
# ============================================================================


class Dataset(BaseModel):
    """Dataset entity within a project"""

    id: str | None = None
    name: str
    project: "Project | str"
    description: str = ""
    variables: list[Variable] = []
    experiments: list[Experiment] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty"""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class Project(BaseModel):
    """Project entity

    Attributes:
        id: Unique identifier
        name: Project name
        description: Project description
        project_type: Type of project (cultivation or spectroscopy)
        process_format: Process format
        product: Associated product
    """

    id: str | None = None
    name: str
    description: str = ""
    project_type: Literal["cultivation", "spectroscopy"]
    process_format: Literal["mammalian", "microbial"] | None = None
    product: Product | str | None = None

    def get_models(
        self,
        client: "DataHowLabClient",
        name: str | None = None,
        model_type: Literal["propagation", "historical"] | None = None,
    ) -> list["Model"]:
        """Get models for this project

        Args:
            client: DataHowLabClient instance
            name: Optional model name filter
            model_type: For cultivation projects, specify propagation or historical

        Returns:
            List of Model objects
        """
        return client.list_models(project=self, name=name, model_type=model_type)

    def get_datasets(
        self, client: "DataHowLabClient", name: str | None = None
    ) -> list[Dataset]:
        """Get datasets for this project

        Args:
            client: DataHowLabClient instance
            name: Optional dataset name filter

        Returns:
            List of Dataset objects
        """
        return client.list_datasets(project=self, name=name)


class Model(BaseModel):
    """Base model entity

    Attributes:
        id: Unique identifier
        name: Model name
        status: Model training status
        project: Parent project ID or Project object
        model_type: Type of model (spectra, propagation, or historical)
        dataset: Optional associated dataset
        config: Optional model configuration
    """

    id: str | None = None
    name: str
    status: str
    project: Project | str
    model_type: Literal["spectra", "propagation", "historical"]
    dataset: Dataset | None = None
    config: dict[str, Any] | None = None

    @property
    def is_ready(self) -> bool:
        """Check if model is ready for predictions"""
        return self.status in ("ready", "success")

    @property
    def input_variables(self) -> list[Variable]:
        """Get input variables for the model"""
        if not self.config or not self.dataset:
            return []
        inputs = self.config.get("groups", {}).get("Inputs", [])
        return [v for v in self.dataset.variables if v.id in inputs]

    @property
    def output_variables(self) -> list[Variable]:
        """Get output variables for the model"""
        if not self.config or not self.dataset:
            return []
        outputs = self.config.get("groups", {}).get("Outputs", [])
        return [v for v in self.dataset.variables if v.id in outputs]

    def predict(
        self,
        client: "DataHowLabClient",
        input_data: SpectraPredictionInput
        | PropagationPredictionInput
        | HistoricalPredictionInput,
    ) -> PredictionOutput:
        """Make predictions using this model

        Args:
            client: DataHowLabClient instance
            input_data: Prediction input (type depends on model type)

        Returns:
            PredictionOutput with predictions and metadata

        Raises:
            ValueError: If model is not ready or input type doesn't match model type
            PredictionError: If prediction fails
        """
        from dhl_sdk.errors import ValidationError

        if not self.is_ready:
            raise ValidationError(
                f"Model '{self.name}' is not ready for predictions (status: {self.status})",
                field="status",
                value=self.status,
            )

        # Type checking
        expected_types = {
            "spectra": SpectraPredictionInput,
            "propagation": PropagationPredictionInput,
            "historical": HistoricalPredictionInput,
        }

        expected = expected_types[self.model_type]
        if not isinstance(input_data, expected):
            raise ValidationError(
                f"Model type '{self.model_type}' requires {expected.__name__} input",
                field="input_data",
                value=type(input_data).__name__,
            )

        return client._predict(model=self, input_data=input_data)
