"""API Entities Module

This module provides a comprehensive set of Pydantic models that represent
multiple entities that can be downloaded or uploaded to the DataBase through
the API .

Classes:
    - Experiment: Represents a structure for experiments
    - Recipe: Represents a structure for recipes
    - Variable: Represents a structure for variables present in experiments and recipes
    - Product: Represents a structure for products present in experiments and recipes
    """

# pylint: disable=no-member, protected-access, too-many-arguments, too-many-lines

import copy
import csv
from abc import ABC, abstractmethod
from enum import Enum
from io import StringIO
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, PrivateAttr, model_validator
from requests import Response

from dhl_sdk._constants import (
    EXPERIMENTS_URL,
    FILES_URL,
    PROCESS_FORMAT_MAP,
    PROCESS_UNIT_MAP,
    PRODUCTS_URL,
    RECIPES_URL,
    VARIABLES_URL,
)

from dhl_sdk._utils import VariableGroupCodes
from dhl_sdk.crud import Client, CRUDClient, DataBaseClient
from dhl_sdk.exceptions import (
    ImportValidationException,
    InvalidVariantException,
    NewEntityException,
)
from dhl_sdk.importers import RunFileImporter, SpectraFileImporter
from dhl_sdk.validators import (
    AbstractFileValidator,
    AbstractValidator,
    ExperimentFileValidator,
    ExperimentValidator,
    ProductValidator,
    RecipeFileValidator,
    SpectraFileValidator,
    VariableValidator,
)


class DataBaseEntity(ABC):
    """Abstract class for DataBase Entities

    Database Entities are the entities that can be pushed and pulled
    directly from the database.
    """

    @abstractmethod
    def validate_import(self, client: Client) -> bool:
        """Validate the entity for importing"""

    @abstractmethod
    def create_request_body(self) -> dict:
        """Create request body for creating the entity"""

    @staticmethod
    @abstractmethod
    def requests(client: Client) -> CRUDClient:
        """Return a CRUDClient for the entity"""


class VariableNumeric(BaseModel):
    """Model for Variables that can be caracterized by a numeric value.

    Attributes:
        default: Default value
        minimum: Minimum value
        maximum: Maximum value
        interpolation_method: Interpolation method for the variable

    """

    default: Optional[float] = Field(default=None, alias="default")
    minimum: Optional[float] = Field(default=None, alias="min")
    maximum: Optional[float] = Field(default=None, alias="max")
    interpolation_method: Optional[Literal["linear", "discrete"]] = Field(
        default=None, alias="interpolation"
    )

    @property
    def variant_string(self) -> str:
        """get variant type as string"""
        return "numeric"


class VariableCategorical(BaseModel):
    """Model for Categorical Variables

    Attributes:
        default: Default value
        strict: Strict mode (whether to allow only values from the categories)
        categories: Categories for the variable
    """

    default: Optional[str] = Field(default=None, alias="default")
    strict: Optional[bool] = Field(default=False, alias="strict")
    categories: Optional[list[str]] = Field(default=None, alias="values")

    @property
    def variant_string(self) -> str:
        """get variant type as string"""
        return "categorical"


class VariableLogical(BaseModel):
    """Model for Logical Variables

    Attributes:
        default: Default value
    """

    default: Optional[bool] = Field(default=None, alias="default")

    @property
    def variant_string(self) -> str:
        """get variant type as string"""
        return "logical"


class FlowVariableReference(BaseModel):
    """Model for Flow Variable References with only the ID, used to serialize the data

    Attributes:
        measurement_id: ID of the measurement variable (X Variable)
        concentration_id: ID of concentration variable (Feed Concentration)
        fraction_id: ID of fraction
    """

    measurement_id: str = Field(alias="measurementId")
    concentration_id: Optional[str] = Field(default=None, alias="concentrationId")
    fraction_id: Optional[str] = Field(default=None, alias="fractionId")


class VariableFlow(BaseModel):
    """Model for Flow Variables

    Attributes:
        flow_type: Type of flow variable - can be "bolus", "conti",
            "mbolus", "mconti", "sampling", "bleed", "perfusion"
        step_size: Step size for the flow variable
        volume_id: Volume ID for the flow variable
        references: References for the flow variable
    """

    flow_type: Literal[
        "bolus", "conti", "mbolus", "mconti", "sampling", "bleed", "perfusion"
    ] = Field(default="bolus", alias="type")
    step_size: Optional[int] = Field(default=None, alias="stepSize")
    volume_id: Optional[str] = Field(default=None, alias="volumeId")
    references: list[FlowVariableReference] = Field(alias="references")

    @staticmethod
    def new(
        flow_type: Literal[
            "bolus", "conti", "mbolus", "mconti", "sampling", "bleed", "perfusion"
        ],
        variable_references: list[FlowVariableReference],
        step_size: Optional[int] = None,
        volume_variable_id: Optional[str] = None,
    ) -> "VariableFlow":
        """Create a new Flow Variable from user input

        Parameters
        ----------
        flow_type : Literal["bolus", "conti", "mbolus", "mconti", "sampling", "bleed", "perfusion"]
            Type of flow variable
        variable_references : list[FlowVariableReference]
            References for the flow variable. It must contain at least one reference.
            Each Reference must be of type FlowVariableReference (or a dictionary
            with the same keys)
            FlowVariableReference contains the following keys:
                - measurement_id: ID of the measurement variable (X Variable)
                - concentration_id: ID of concentration variable (Feed Concentration)
        step_size : Optional[int]
            Step size for the flow variable in seconds. This is required for "conti", "mconti",
            "bleed", "perfusion" types
        volume_variable_id : Optional[str]
            Variable ID of the Initial Bioreactor Volume
        """

        if flow_type in ["conti", "mconti", "bleed", "perfusion"]:
            if not step_size:
                raise NewEntityException(
                    "Step size must be provided for 'conti', 'mconti', 'bleed', 'perfusion' types"
                )

        return VariableFlow(
            type=flow_type,
            stepSize=step_size,
            volumeId=volume_variable_id,
            references=variable_references,
        )

    @property
    def variant_string(self) -> str:
        """get variant type as string"""
        return "flow"


class VariableSpectrumXAxis(BaseModel):
    """Pydantic model for variant spectrum x axis"""

    dimension: Optional[int] = Field(default=None, alias="dimension")
    unit: Optional[str] = Field(default=None, alias="unit")
    min: Optional[float] = Field(default=None, alias="min")
    max: Optional[float] = Field(default=None, alias="max")


class VariableSpectrumYAxis(BaseModel):
    """Pydantic model for variant spectrum y axis"""

    label: Optional[str] = Field(default=None, alias="label")


class VariableSpectrum(BaseModel):
    """Pydantic model for variant details spectrum

    Attributes:
        x_axis: X axis description (dimension, unit, min, max)
        y_axis: Y axis description (label)
    """

    x_axis: Optional[VariableSpectrumXAxis] = Field(default=None, alias="xAxis")
    y_axis: Optional[VariableSpectrumYAxis] = Field(default=None, alias="yAxis")

    @property
    def variant_string(self) -> str:
        """get variant type as string"""
        return "spectrum"


VariantDetails = Union[
    VariableNumeric,
    VariableCategorical,
    VariableLogical,
    VariableFlow,
    VariableSpectrum,
]


class Group(BaseModel):
    """Model for Variable Group"""

    id: Optional[str] = Field(default=None, alias="id")
    code: Optional[str] = Field(default=None, alias="code")
    name: Optional[str] = Field(default=None, alias="name")
    aggregation: Optional[str] = Field(default=None, alias="aggregation")

    def validate_group(self, group_codes: dict[str, tuple[str, str]]) -> None:
        """Validate the group"""
        if self.name not in group_codes:
            raise ImportValidationException(
                (
                    f"Variable Group must be one of: {list(group_codes.keys())}."
                    " instead, it got '{self.name}'"
                )
            )

        self.id, self.code = group_codes[self.name]


class Variant(str, Enum):
    """Enum for variants"""

    FLOW = "flow"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    LOGICAL = "logical"
    SPECTRUM = "spectrum"

    def get_variant_details(self, **kwargs) -> VariantDetails:
        """get variant details"""
        if self == Variant.FLOW:
            return VariableFlow(**kwargs)
        if self == Variant.NUMERIC:
            return VariableNumeric(**kwargs)
        if self == Variant.CATEGORICAL:
            return VariableCategorical(**kwargs)
        if self == Variant.LOGICAL:
            return VariableLogical(**kwargs)
        if self == Variant.SPECTRUM:
            return VariableSpectrum(**kwargs)

        raise ValueError(f"Variant {self} not supported")


class Variable(BaseModel, DataBaseEntity):
    """Model Variable"""

    id: Optional[str] = Field(default=None, alias="id")
    name: str = Field(alias="name")
    code: str = Field(alias="code")
    description: Optional[str] = Field(default="", alias="description")
    measurement_unit: Optional[str] = Field(default=None, alias="measurementUnit")
    group: Optional[Group] = Field(default=None, alias="group")
    variant: Variant = Field(alias="variant")
    variant_details: Optional[VariantDetails] = None
    size: Optional[int] = None

    _validator: AbstractValidator = PrivateAttr(VariableValidator())

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def _validate_model_struct(cls, data) -> dict:
        """Validate the structure of the variable"""

        variant = Variant(data["variant"])

        # check if variant details field is in input data
        if "variant_details" not in data:
            variant_details = data.get(variant.value, {})
            data["variant_details"] = variant.get_variant_details(**variant_details)
        else:
            try:
                if data["variant_details"].variant_string != variant.value:
                    raise ValueError(
                        (
                            f"Variant details not valid for {variant} variant."
                            f"Found: {data['variant_details'].variant_string}"
                        )
                    )
            except AttributeError as asc:
                raise ValueError(
                    f"Variant details not valid for {variant} variant"
                ) from asc

        if variant == Variant.SPECTRUM:
            try:
                size = data["spectrum"]["xAxis"]["dimension"]
            except KeyError as err:
                raise KeyError(
                    "The spectrum variable does not have a valid structure"
                ) from err

            data["size"] = size

        return data

    def matches_key(self, key) -> bool:
        """Find the id of the variable"""
        if self.id == key or (self.code is not None and self.code == key):
            return True
        return False

    def __str__(self) -> str:
        """Print only the variable's ID and Code"""
        return f"Name: {self.name} ,  Code: {self.code}"

    def validate_import(self, client: Client) -> bool:
        """Validate the variable for uploading"""

        # validate and update group
        variable_group_codes = VariableGroupCodes(client).get_variable_group_codes()

        if self.group:
            self.group.validate_group(variable_group_codes)
        else:
            raise ImportValidationException(
                "Variable group is not present, please provide a valid group"
            )

        # validate entity
        return self._validator.validate(entity=self, client=client)

    def create_request_body(self) -> dict:
        """Create request body for creating a variable"""

        model_dict = self.model_dump(
            by_alias=True,
            include={
                "code": True,
                "name": True,
                "description": True,
                "measurement_unit": True,
                "group": {"id"},
            },
        )

        model_dict["variant"] = self.variant.value

        if self.variant_details:
            model_dict[self.variant.value] = self.variant_details.model_dump(
                by_alias=True, exclude_none=True
            )
        else:
            model_dict[self.variant.value] = {}

        return model_dict

    def is_imported(self, client: Client) -> bool:
        """Check if the variable is already imported"""

        if not self.id:
            return False

        response = client.get(f"{VARIABLES_URL}/{self.id}")
        return response.status_code == 200

    @staticmethod
    def get_valid_variable_groups(client: DataBaseClient) -> list[str]:
        """Get the valid variable groups from the database

        It is a helper function to assist with the creation of new variables.
        """
        group_codes = VariableGroupCodes(client._client).get_variable_group_codes()
        return list(group_codes.keys())

    @staticmethod
    def new(
        code: str,
        name: str,
        measurement_unit: str,
        variable_group: str,
        variable_type: Union[
            VariableNumeric,
            VariableCategorical,
            VariableLogical,
            VariableFlow,
            VariableSpectrum,
        ],
        description: Optional[str] = "",
    ) -> "Variable":
        """Create a new variable from user input

        Parameters
        ----------
        code : str
            Code of the variable
        name : str
            Name of the variable
        measurement_unit : str
            Measurement unit of the variable
        variable_group : str
            Group of the variable
        variable_type : Union[VariableNumeric,
                              VariableCategorical,
                              VariableLogical,
                              VariableFlow,
                              VariableSpectrum]
            Type of the variable
        description : Optional[str]
            Description of the variable

        Returns
        -------
        Variable
            A new variable with the given parameters
        """

        code = code.strip()
        name = name.strip()
        measurement_unit = measurement_unit.strip()
        variable_group = variable_group.strip()

        if code == "":
            raise NewEntityException("Variable code can not be empty")

        if name == "":
            raise NewEntityException("Variable name can not be empty")

        if measurement_unit == "":
            raise NewEntityException("Measurement unit can not be empty")

        if variable_group == "":
            raise NewEntityException("Variable group can not be empty")

        var_dict = {
            "code": code,
            "name": name,
            "description": description if description is not None else "",
            "variant": variable_type.variant_string,
            "measurementUnit": measurement_unit,
            "group": {
                "name": variable_group,
            },
            "variant_details": variable_type,
        }

        return Variable(**var_dict)

    @staticmethod
    def requests(client: Client) -> CRUDClient["Variable"]:
        # pylint: disable=missing-function-docstring
        return CRUDClient["Variable"](client, VARIABLES_URL, Variable)


class Product(BaseModel, DataBaseEntity):
    """Pydantic model for Product"""

    id: Optional[str] = Field(default=None, alias="id")
    code: str = Field(alias="code")
    name: str = Field(alias="name")
    description: Optional[str] = Field(default="", alias="description")
    process_format_id: Optional[str] = Field(
        default=PROCESS_FORMAT_MAP["mammalian"], alias="processFormatId"
    )

    _validator: AbstractValidator = PrivateAttr(ProductValidator())

    def validate_import(self, client: Client) -> bool:
        """Validate if the product can be imported"""
        return self._validator.validate(entity=self, client=client)

    def create_request_body(self) -> dict:
        """Create request body for creating a product"""
        return self.model_dump(exclude_none=True, by_alias=True, exclude={"id"})

    @staticmethod
    def new(
        code: str,
        name: str,
        description: Optional[str] = "",
        process_format: Literal["mammalian", "microbial"] = "mammalian",
    ) -> "Product":
        """Create a new Product from user input

        Parameters
        ----------
        code : str
            Code of the product (must be unique and from 1 to 6 characters long)
        name : str
            Name of the product
        description : Optional[str]
            Description of the product
        process_format : Literal["mammalian", "microbial"]
            The format of the process. Defaults to "mammalian".

        Returns
        -------
        Product
            A new product with the given parameters

        """

        code = code.strip()
        name = name.strip()

        if code == "":
            raise NewEntityException("Product code cannot be empty")

        if name == "":
            raise NewEntityException("Product name cannot be empty")

        if len(code) > 6:
            raise NewEntityException("Product code must be from 1 to 6 characters long")

        if process_format not in PROCESS_FORMAT_MAP:
            raise ValueError(
                f"Format must be one of {list(PROCESS_FORMAT_MAP.keys())}, "
                "but got '{process_format}'"
            )
        format_id = PROCESS_FORMAT_MAP[process_format]

        return Product(
            code=code, name=name, description=description, processFormatId=format_id
        )

    @staticmethod
    def requests(client: Client) -> CRUDClient["Product"]:
        # pylint: disable=missing-function-docstring
        return CRUDClient["Product"](client, PRODUCTS_URL, Product)


class File(BaseModel):
    """Pydantic model for File"""

    id: Optional[str] = Field(default=None, alias="id")
    name: str = Field(alias="name")
    description: str = Field(alias="description")
    type: str = Field(alias="type")
    variant: Literal["run", "samples"] = Field(default="run", alias="variant")

    _data: dict[str, dict[str, list]] = PrivateAttr()
    _validator: AbstractFileValidator = PrivateAttr(ExperimentFileValidator())

    def __init__(self, **data):
        super().__init__(**data)
        self._data = data["data"]
        self._validator = data["validator"]

    def validate_import(
        self, variables: list[Variable], variant_details: Optional[dict] = None
    ) -> bool:
        """Validate if the file can be imported"""
        if self._validator.validate(
            variables=variables,
            data=self._data,
            variant=self.variant,
            variant_details=variant_details,
        ):
            self._data = self._validator.format_data(
                variables=variables, data=self._data
            )
            return True

        return False

    def create_request_body(self) -> dict:
        """Create request body for creating a file"""

        file_dict = self.model_dump(
            exclude_none=True,
            by_alias=True,
            include={"name": True, "description": True},
        )

        suffix = "Data"
        if self.type == "spectra":
            suffix = "Spectra"

        if self.variant == "run":
            file_dict["type"] = f"run{suffix}"
        elif self.variant == "samples":
            file_dict["type"] = f"sample{suffix}"

        return file_dict

    def create_file(self, client: Client) -> Optional[Union[str, tuple[str, str]]]:
        """Create a file in the database"""

        if self.type == "run":
            importer = RunFileImporter(client)
        elif self.type == "spectra":
            importer = SpectraFileImporter(client)
        else:
            raise ValueError("File type must be either 'run' or 'spectra'")

        file_id = importer.import_file(self)

        return file_id

    @staticmethod
    def requests(client: Client) -> CRUDClient["File"]:
        # pylint: disable=missing-function-docstring
        return CRUDClient["File"](client, FILES_URL, File)

    @staticmethod
    def download(client: Client, file_id: str) -> Response:
        # pylint: disable=missing-function-docstring
        return client.get(f"{FILES_URL}/{file_id}/data")


class Instances(BaseModel):
    """Pydantic model for Unresolved Instances"""

    column: str = Field(alias="column")
    fileId: str = Field(alias="fileId")


class Recipe(BaseModel, DataBaseEntity):
    """Pydantic model for Recipe"""

    id: Optional[str] = Field(default=None, alias="id")
    name: str = Field(alias="name")
    description: Optional[str] = Field(default=None, alias="description")
    process_unit_id: Optional[str] = Field(default=None, alias="processUnitId")
    process_format_id: Optional[str] = Field(default=None, alias="processFormatId")
    product: Product = Field(alias="product")
    duration: Optional[int] = Field(default=None, alias="duration")
    variables: list[Variable] = Field(alias="variables")
    instances: list[Instances] = Field(alias="instances")
    file_data: Optional[File] = None

    _validator: AbstractValidator = PrivateAttr(ExperimentValidator())

    def create_request_body(self) -> dict:
        """Create request body for creating an experiment"""

        model_dict = self.model_dump(
            by_alias=True,
            include={
                "name": True,
                "description": True,
                "duration": True,
                "product": {"id"},
                "variables": {"__all__": {"id"}},
                "instances": {"__all__": {"column", "fileId"}},
            },
        )

        return model_dict

    def validate_import(self, client: Client) -> bool:
        """Validate if the recipe can be imported"""

        if not self._validator.validate(entity=self, client=client):
            return False

        file_id = None
        if self.file_data.validate_import(self.variables):
            file_id = self.file_data.create_file(client)

        if not file_id:
            raise ImportValidationException("File data could not be imported")

        for variable in self.variables:
            self.instances.append(Instances(column=variable.code, fileId=file_id))

        return True

    @staticmethod
    def new(
        name: str,
        description: str,
        product: Product,
        variables: list[Variable],
        data: dict,
        duration: Optional[int] = None,
    ) -> "Recipe":
        """Create a new Recipe from user input

        Parameters
        ----------
        name : str
            Name of the recipe
        description : str
            Description of the recipe
        product : Product
            Product associated to the recipe (needs to be created before)
        variables : list[Variable]
            List of variables associated to the recipe (needs to be created before)
        data : dict
            Data to be uploaded to the recipe (dictionary)
        duration : Optional[int]
            Duration of the recipe

        Returns
        -------
        Recipe
            A new recipe with the given parameters

        """

        name = name.strip()
        if name == "":
            raise NewEntityException("Recipe name cannot be empty")

        # Create a new Data File
        file = File(
            name=name,
            description=description,
            type="run",
            data=copy.deepcopy(data),
            validator=RecipeFileValidator(duration=duration),
        )

        # Create a new Experiment
        recipe = Recipe(
            name=name,
            description=description,
            duration=duration,
            product=product,
            variables=variables,
            instances=[],
            file_data=file,
        )

        return recipe

    @staticmethod
    def requests(client: Client) -> CRUDClient["Recipe"]:
        # pylint: disable=missing-function-docstring
        return CRUDClient["Recipe"](client, RECIPES_URL, Recipe)


class Experiment(BaseModel, DataBaseEntity):
    """Pydantic model for Experiment"""

    id: Optional[str] = Field(default=None, alias="id")
    name: str = Field(alias="name")
    description: str = Field(alias="description")
    process_unit_id: Optional[str] = Field(
        default=PROCESS_UNIT_MAP["cultivation"], alias="processUnitId"
    )
    process_format_id: Optional[str] = Field(
        default=PROCESS_FORMAT_MAP["mammalian"], alias="processFormatId"
    )
    product: Product = Field(alias="product")
    subunit: str = Field(default="", alias="subunit")
    variables: list[Variable] = Field(alias="variables")
    instances: list[Instances] = Field(alias="instances")
    variant: Literal["run", "samples"] = Field(default="run", alias="variant")

    variant_details: Optional[dict] = None
    file_data: Optional[File] = None

    _validator: AbstractValidator = PrivateAttr(ExperimentValidator())

    def create_request_body(self) -> dict:
        """Create request body for creating an experiment"""
        model_dict = self.model_dump(
            by_alias=True,
            include={
                "name": True,
                "description": True,
                "subunit": True,
                "process_format_id": True,
                "process_unit_id": True,
                "product": {"id"},
                "variables": {"__all__": {"id"}},
                "instances": {"__all__": {"column", "fileId"}},
                "variant": True,
            },
        )

        model_dict[self.variant] = self.variant_details

        return model_dict

    def validate_import(self, client: Client) -> bool:
        """Validate if the experiment can be imported"""

        if not self._validator.validate(entity=self, client=client):
            return False

        file_id = None
        if self.file_data.validate_import(self.variables, self.variant_details):
            file_id = self.file_data.create_file(client)

        if not file_id:
            raise ImportValidationException("File data could not be imported")

        # if file_id is a tuple, it means that the file is a spectra file
        if isinstance(file_id, tuple):
            self.instances.append(Instances(column="1", fileId=file_id[0]))
            file_id = file_id[1]

        for variable in self.variables:
            # skip if variable is spectra
            if variable.variant == Variant.SPECTRUM:
                continue
            self.instances.append(Instances(column=variable.code, fileId=file_id))

        return True

    def get_data(self, client: DataBaseClient) -> dict:
        """Get experiment data from the API

        Parameters
        ----------
        client : DataBaseClient
            Client to use to get the data, i.e., DataHowLabClient

        Returns
        -------
        Dictionary with the data where:
            key: variable code
            value: a dictionary with the data for the variable, with "timestamps" and "values" keys

        Example:
        --------
        >>> client = DataHowLabClient()
        >>> data = experiment.get_data(client)
        >>> print(data)
        {'var1': {"timestamps": [1,2,3], "values": [1.1, 2.2, 3.3]},
        'var2': {"timestamps": [1,2,3], "values": [10.1, 12.2, 33.3]}}

        """

        cache = {}
        experiment_data = {}

        for instance, variable in zip(self.instances, self.variables):
            if instance.fileId not in cache:
                response = File.download(client._client, instance.fileId)
                cache[instance.fileId] = response
            else:
                response = cache[instance.fileId]

            if instance.column in experiment_data:
                continue

            if response.headers["content-type"] == "application/json":
                data = response.json()
                experiment_data[variable.code] = data["timeseries"][instance.column]

            elif response.headers["content-type"] == "text/csv":
                csv_data = list(csv.reader(StringIO(response.text)))

                ids = [row[0] for row in csv_data]
                if self.variant == "run":  # run variant
                    spectra_ids = "timestamps"
                elif self.variant == "samples":  # samples variant
                    spectra_ids = "sampleId"
                else:
                    raise InvalidVariantException()

                data_rows = [row[1:] for row in csv_data]
                experiment_data["spectra"] = {
                    spectra_ids: ids,
                    "values": data_rows,
                }

        return experiment_data

    @staticmethod
    def new(
        name: str,
        description: str,
        product: Product,
        variables: list[Variable],
        data: dict,
        process_format: Literal["mammalian", "microbial"] = "mammalian",
        data_type: Literal["run", "spectra"] = "run",
        variant: Literal["run", "samples"] = "run",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> "Experiment":
        """Create a new Experiment from user input

        Parameters
        ----------
        name : str
            Name of the experiment
        description : str
            Description of the experiment
        product : Product
            Product associated to the experiment (needs to be created before)
        variables : list[Variable]
            List of variables associated to the experiment (needs to be created before)
        data_type : Literal["run", "spectra"]
            Type of data to be uploaded ("run" or "spectra")
        data : dict
            Data to be uploaded to the experiment (dictionary).
            The data must be a dictionary with the variable codes as keys.
            For "spectra" variant, the data must be a dictionary with the variable codes
                as keys and a list of lists of values as values.
        process_format : Literal["mammalian", "microbial"]
            The format of the process. Defaults to "mammalian".
        variant : Literal["run", "samples"]
            Variant of the experiment ("run" or "samples").
            "run" is for time series data and "samples" is for sampled data
        start_time : Optional[str]
            Start time of the experiment (only for "run" variant)
        end_time : Optional[str]
            End time of the experiment (only for "run" variant)

        Returns
        -------
        Experiment
            A new experiment with the given parameters

        """

        name = name.strip()
        if name == "":
            raise NewEntityException("Experiment name cannot be empty")

        if variant == "run" and (not start_time or not end_time):
            raise NewEntityException(
                "Start time and end time must be provided for 'run' variant"
            )

        if process_format not in PROCESS_FORMAT_MAP:
            raise ValueError(
                f"Format must be one of {list(PROCESS_FORMAT_MAP.keys())}, "
                "but got '{process_format}'"
            )
        format_id = PROCESS_FORMAT_MAP[process_format]

        file_validator_class = (
            SpectraFileValidator if data_type == "spectra" else ExperimentFileValidator
        )
        file_validator = file_validator_class()

        # Create a new Data File
        file = File(
            name=name,
            description=description,
            type=data_type,
            variant=variant,
            data=copy.deepcopy(data),
            validator=file_validator,
        )

        variant_details = (
            {"startTime": start_time, "endTime": end_time} if variant == "run" else {}
        )

        # Create a new Experiment
        return Experiment(
            name=name,
            description=description,
            product=product,
            processFormatId=format_id,
            variables=variables,
            instances=[],
            file_data=file,
            variant=variant,
            variant_details=variant_details,
        )

    @staticmethod
    def requests(client: Client) -> CRUDClient["Experiment"]:
        # pylint: disable=missing-function-docstring
        return CRUDClient["Experiment"](client, EXPERIMENTS_URL, Experiment)
