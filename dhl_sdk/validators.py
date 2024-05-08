""" New Entity Validators"""

# pylint: disable=missing-function-docstring, arguments-differ
# pylint: disable=missing-class-docstring, protected-access

import math
import warnings
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, Union

from dhl_sdk._input_processing import (
    groupcode_is_output,
    groupcode_is_timedependent,
    variant_is_numeric,
)
from dhl_sdk._utils import FILES_URL, PRODUCTS_URL, VARIABLES_URL, is_date_in_format
from dhl_sdk.crud import Client, CRUDClient
from dhl_sdk.exceptions import ImportValidationException


class AbstractValidator(ABC):
    """Abstract class for Validators"""

    @abstractmethod
    def validate(self, **kwargs) -> bool:
        """Validate the entity for importing"""

    @abstractmethod
    def is_imported(self, **kwargs) -> bool:
        """Check if the entity is already imported"""


class Group(Protocol):
    id: str
    name: str
    code: str


class Variable(Protocol):
    id: str
    code: str
    name: str
    group: Group
    measurement_unit: str
    _validator: AbstractValidator


class Product(Protocol):
    id: str
    code: str
    name: str
    _validator: AbstractValidator


class File(Protocol):
    id: str
    name: str
    type: str


class Experiment(Protocol):
    id: str
    product: Product
    variables: list[Variable]
    file_data: Any
    _validator: AbstractValidator

    @staticmethod
    def requests(client: Client) -> CRUDClient["Experiment"]:
        # pylint: disable=missing-function-docstring
        ...


class Recipe(Protocol):
    id: str
    product: Product
    variables: list[Variable]
    file_data: Any
    _validator: AbstractValidator

    @staticmethod
    def requests(client: Client) -> CRUDClient["Recipe"]:
        # pylint: disable=missing-function-docstring
        ...


class VariableValidator(AbstractValidator):
    """Validator for Variables"""

    def validate(self, entity: Variable, client: Client) -> bool:
        """Validate the variable for importing"""

        # remove whitespaces from code
        entity.code = entity.code.strip()

        # first validate if variable is alredy in the DB
        if self.is_imported(entity, client):
            warnings.simplefilter("always")
            warnings.warn(
                f"Variable {entity.code} is already present in the DB. Skipping import."
            )
            return False

        validation_errors = []

        # validate if variable code already exists
        query_params = {
            "filterBy[code]": entity.code,
            "filterBy[group._id]": entity.group.id,
            "archived": "any",
        }

        response = client.get(VARIABLES_URL, query_params=query_params)
        if int(response.headers.get("x-total-count")) > 0:  # type: ignore
            validation_errors.append(f"The variable code {entity.code} already exists")

        # Validate if variable name already exists
        query_params = {
            "filterBy[name]": entity.name,
            "filterBy[group._id]": entity.group.id,
            "archived": "any",
        }

        response = client.get(VARIABLES_URL, query_params=query_params)
        if int(response.headers.get("x-total-count")) > 0:  # type: ignore
            validation_errors.append(f"The variable name {entity.name} already exists")

        # Validate if measurement unit is present
        if entity.measurement_unit is None:
            validation_errors.append("The measurement unit must be present")

        if validation_errors:
            raise ImportValidationException("\n".join(validation_errors))

        return True

    def is_imported(self, entity: Variable, client: Client) -> bool:
        """Check if the variable is already imported"""

        # check if variable has no id. If it has no id, check if there is already a variable
        # with the same code, name and group in the DB. If so, set the id of the variable
        # and return True

        if not entity.id:
            query_params = {
                "filterBy[code]": entity.code,
                "filterBy[name]": entity.name,
                "filterBy[measurementUnit]": entity.measurement_unit,
                "filterBy[group._id]": entity.group.id,
                "archived": "any",
            }

            response = client.get(VARIABLES_URL, query_params=query_params)
            if int(response.headers.get("x-total-count")) > 0:
                entity.id = response.json()[0]["id"]
                return True
            else:
                return False

        response = client.get(f"{VARIABLES_URL}/{entity.id}")
        return response.status_code == 200


class ProductValidator(AbstractValidator):
    """Validator for Products"""

    def validate(self, entity: Product, client: Client) -> bool:
        validation_errors = []

        # remove whitespaces from code
        entity.code = entity.code.strip()

        if self.is_imported(entity, client):
            warnings.simplefilter("always")
            warnings.warn(
                f"Product {entity.code} is already present in the DB. Skipping import."
            )
            return False

        # check if length of code is less than 5
        if len(entity.code) > 5:
            raise ImportValidationException(
                "Product code must be from 1 to 5 characters long"
            )

        # validate if variable code already exists
        query_params = {
            "filterBy[code]": entity.code,
            "archived": "any",
        }

        response = client.get(PRODUCTS_URL, query_params=query_params)
        if int(response.headers.get("x-total-count")) > 0:
            validation_errors.append(
                f"This product code {entity.code} is already taken"
            )

        # Validate if variable name already exists
        query_params = {
            "filterBy[name]": entity.name,
            "archived": "any",
        }

        response = client.get(PRODUCTS_URL, query_params=query_params)
        if int(response.headers.get("x-total-count")) > 0:
            validation_errors.append(
                f"This product name {entity.name} is already taken"
            )

        if validation_errors:
            raise ImportValidationException("\n".join(validation_errors))

        return True

    def is_imported(self, entity: Product, client: Client) -> bool:
        """Check if the variable is already imported"""

        if not entity.id:
            query_params = {
                "filterBy[code]": entity.code,
                "filterBy[name]": entity.name,
                "archived": "any",
            }

            response = client.get(PRODUCTS_URL, query_params=query_params)
            if int(response.headers.get("x-total-count")) > 0:
                entity.id = response.json()[0]["id"]
                return True
            else:
                return False

        response = client.get(f"{PRODUCTS_URL}/{entity.id}")
        return response.status_code == 200


class AbstractFileValidator(ABC):
    """Abstract class for File Validators"""

    @classmethod
    @abstractmethod
    def format_data(cls, variables: list[Variable], data: Any) -> Any:
        """Format the file data"""

    @abstractmethod
    def validate(self, variables: list[Variable], data: Any, **kwargs) -> bool:
        """Validate the file for importing"""

    @abstractmethod
    def is_imported(self, entity: File, client: Client) -> bool:
        """Check if the file is already imported"""


class RecipeFileValidator(AbstractFileValidator):
    """Validator for Files"""

    def __init__(self, duration: Optional[int] = None) -> None:
        super().__init__()
        self.duration = duration

    @classmethod
    def format_data(cls, variables: list[Variable], data: Any) -> Any:
        """Format the file data"""

        # only store the first value of X Variables
        for variable in variables:
            if variable.group.code == "X" and variable.code in data:
                if len(data[variable.code]["timestamps"]) > 1:
                    warnings.warn(
                        f"Variable {variable.code} has more than 1 timestamp."
                        " Only the first value will be stored"
                    )

                    data[variable.code]["timestamps"] = [
                        data[variable.code]["timestamps"][0]
                    ]
                    data[variable.code]["values"] = [data[variable.code]["values"][0]]

        return data

    def validate(self, variables: list[Variable], data: Any) -> bool:
        """Validate the file for importing"""
        validation_errors = []

        # check if there are X variables
        if not any(var.group.code == "X" for var in variables):
            raise ImportValidationException(
                (
                    "No variables 'X' found. 'X' variables"
                    " are mandatory for the recipe."
                )
            )

        timedependent_variable_size = None

        for variable in variables:
            if variable.code in data:
                # check if there are output varlues
                if groupcode_is_output(variable.group.code):
                    validation_errors.append(
                        f"Variable {variable.code} is an Output,"
                        " so it's not allowed in the recipe"
                    )
                    continue

                # check if , for feedConc variables, the corresponding feed
                # and X variables are present
                if variable.group.code == "FeedConc":
                    var_code = variable.code
                    feedconc_codes = var_code.split("_")
                    if len(feedconc_codes) != 2:
                        validation_errors.append(
                            f"Variable {variable.code} must have the format 'Feed_XVar'"
                        )
                        continue

                    if feedconc_codes[0] not in data.keys():
                        validation_errors.append(
                            f"Variable {variable.code} does not have a corresponding Feed Variable"
                        )
                        continue

                    if feedconc_codes[1] not in data.keys():
                        validation_errors.append(
                            f"Variable {variable.code} does not have a corresponding X Variable"
                        )
                        continue

                variable_data = data[variable.code]
                if not isinstance(variable_data, dict):
                    validation_errors.append(
                        (
                            f"Variable {variable.code} data must be a dictionary with"
                            "the mandatory fields 'timestamps' and 'values'"
                        )
                    )
                    continue

                if "timestamps" not in variable_data or "values" not in variable_data:
                    validation_errors.append(
                        f"Variable {variable.code} data must contain 'timestamps' and 'values' key"
                    )
                    continue

                timestamps = variable_data["timestamps"]
                values = variable_data["values"]

                if not isinstance(timestamps, list) or not isinstance(values, list):
                    validation_errors.append(
                        (
                            f"Variable {variable.code} data must "
                            " contain 'timestamps' and 'values' as lists"
                        )
                    )
                    continue

                if len(values) != len(timestamps) or len(timestamps) == 0:
                    validation_errors.append(
                        (
                            f"Variable {variable.code} data can't "
                            " be empty and must have equal length "
                            "of timestamps and values"
                        )
                    )
                    continue

                if None in values:
                    validation_errors.append(
                        (
                            f"Variable {variable.code} contains None values, that are not allowed"
                        )
                    )
                    continue

                if groupcode_is_timedependent(variable.group.code):
                    if len(timestamps) < 2:
                        validation_errors.append(
                            (
                                f"Variable {variable.code} must have the"
                                " more than 1 timestamp"
                            )
                        )
                        continue

                    if timedependent_variable_size is None:
                        timedependent_variable_size = len(timestamps)
                    else:
                        if len(timestamps) != timedependent_variable_size:
                            validation_errors.append(
                                (
                                    f"Variable {variable.code} must have the"
                                    " same length as the other time "
                                    " dependent variables {timedependent_variable_size}"
                                )
                            )
                            continue

                    if self.duration:
                        if (timestamps[-1] - timestamps[0]) != self.duration:
                            validation_errors.append(
                                (
                                    f"Variable {variable.code} timestamps must"
                                    " have the duration of the recipe"
                                )
                            )
                            continue

                else:
                    # validate if non time dependent inputs have length of 1 (only initial values)
                    if len(values) != 1 and variable.group.code != "X":
                        validation_errors.append(
                            (
                                f"Input {variable.code} only requires initial "
                                f"values, so it must have a length of 1"
                            )
                        )
                        continue

                if variant_is_numeric(variable.variant):
                    if not all(
                        isinstance(value, (int, float)) and math.isfinite(value)
                        for value in values
                    ):
                        validation_errors.append(
                            (f"Variable {variable.code} values must be numeric")
                        )
                        continue

            else:
                if groupcode_is_output(variable.group.code):
                    continue

                validation_errors.append(
                    f"Variable {variable.code} is missing from the data dictionary"
                )

        if validation_errors:
            raise ImportValidationException("\n".join(validation_errors))

        return True

    def is_imported(self, entity: File, client: Client) -> bool:
        """Check if the file is already imported"""

        if not entity.id:
            return False

        response = client.get(f"{FILES_URL}/{entity.id}")
        return response.status_code == 200


class ExperimentFileValidator(AbstractFileValidator):
    """Validator for Files"""

    @classmethod
    def format_data(cls, variables: list, data: Any) -> Any:
        """Format the file data"""
        return data

    def validate(
        self, variables: list[Variable], data: Any, variant: str = "run"
    ) -> bool:
        """Validate the file for importing"""
        validation_errors = []

        if variant == "run":
            sample_id = "timestamps"
        elif variant == "samples":
            sample_id = "sampleId"

        for variable in variables:
            if variable.code.lower() not in (key.lower() for key in data):
                validation_errors.append(
                    f"Variable {variable.code} is missing from the data dictionary"
                )
                continue

            variable_data = data[variable.code]
            if not isinstance(variable_data, dict):
                validation_errors.append(
                    (
                        f"Variable {variable.code} data must be a dictionary with"
                        "the mandatory fields 'timestamps' and 'values'"
                    )
                )
                continue

            if sample_id not in variable_data or "values" not in variable_data:
                validation_errors.append(
                    f"Variable {variable.code} data must contain {sample_id} and 'values' key"
                )
                continue

            ids = variable_data[sample_id]
            values = variable_data["values"]

            if not isinstance(ids, list) or not isinstance(values, list):
                validation_errors.append(
                    f"Variable {variable.code} data must contain {sample_id} and 'values' as lists"
                )
                continue

            if len(ids) != len(values) or len(ids) == 0:
                validation_errors.append(
                    (
                        f"Variable {variable.code} data can't be empty and must have equal length"
                        f"of {sample_id} and values"
                    )
                )
                continue

        if validation_errors:
            raise ImportValidationException("\n".join(validation_errors))

        return True

    def is_imported(self, entity: File, client: Client) -> bool:
        """Check if the file is already imported"""

        if not entity.id:
            return False

        response = client.get(f"{FILES_URL}/{entity.id}")
        return response.status_code == 200


class SpectraFileValidator(AbstractFileValidator):
    """Validator for Files"""

    @classmethod
    def format_data(cls, variables: list, data: Any) -> Any:
        """Format the file data"""
        return data

    def validate(
        self, variables: list[Variable], data: Any, variant: str = "run"
    ) -> bool:
        """Validate the file for importing"""
        validation_errors = []

        if variant == "run":
            sample_id = "timestamps"
        elif variant == "samples":
            sample_id = "sampleId"

        if "spectra" not in data:
            raise ImportValidationException(
                ("Spectra data is missing. Please add the 'spectra' key to the data")
            )

        # save spectra variable in variable list
        spectra_variable = None
        for variable in variables:
            if variable.group.code == "SPC":
                if spectra_variable is not None:
                    raise ImportValidationException(
                        "Only one variable of the group Spectra is allowed"
                    )
                spectra_variable = variable
                variable_code = "spectra"

            else:
                variable_code = variable.code
                if variable.code.lower() not in (key.lower() for key in data):
                    validation_errors.append(
                        f"Variable {variable.code} is missing from the data dictionary"
                    )
                    continue

            variable_data = data[variable_code]
            if not isinstance(variable_data, dict):
                validation_errors.append(
                    (
                        f"Variable {variable_code} data must be a dictionary with"
                        f"the mandatory fields {sample_id} and 'values'"
                    )
                )
                continue

            if sample_id not in variable_data or "values" not in variable_data:
                validation_errors.append(
                    f"Variable {variable_code} data must contain {sample_id} and 'values' key"
                )
                continue

            ids = variable_data[sample_id]
            values = variable_data["values"]

            if not isinstance(ids, list) or not isinstance(values, list):
                validation_errors.append(
                    f"Variable {variable_code} data must contain {sample_id} and 'values' as lists"
                )
                continue

            if len(ids) != len(values) or len(ids) == 0:
                validation_errors.append(
                    (
                        f"Variable {variable_code} data can't be empty and must have equal length"
                        f"of {sample_id} and values"
                    )
                )
                continue

            if variable_code == "spectra":
                if sample_id == "timestamps":
                    for date in ids:
                        if not is_date_in_format(date, "%Y-%m-%dT%H:%M:%S.%fZ"):
                            validation_errors.append(
                                f"Timestamp {date} is not in the correct format."
                                "The timestamp must be in the format %Y-%m-%dT%H:%M:%S.%fZ"
                            )
                            continue

                if not all(isinstance(value, list) for value in values):
                    validation_errors.append(
                        f"Variable {variable_code} values must be a list of lists"
                    )
                    continue

                spectra_size = variable.size
                for i, value in enumerate(values):
                    if len(value) != spectra_size:
                        validation_errors.append(
                            (
                                f"Spectrum of index {i} has the wrong dimensions."
                                f"It should be of length {spectra_size}"
                            )
                        )
                        continue

                    if not all(isinstance(val, (int, float)) for val in value):
                        validation_errors.append(
                            f"Variable {variable_code} values must all be numeric"
                        )
                        continue

        if spectra_variable is None:
            raise ImportValidationException(
                "A variable of the group Spectra is missing from the variable list"
            )

        if validation_errors:
            raise ImportValidationException("\n".join(validation_errors))

        return True

    def is_imported(self, entity: File, client: Client) -> bool:
        """Check if the file is already imported"""

        if not entity.id:
            return False

        response = client.get(f"{FILES_URL}/{entity.id}")
        return response.status_code == 200


class ExperimentValidator(AbstractValidator):
    """Validator for Experiments"""

    def validate(self, entity: Union[Experiment, Recipe], client: Client) -> bool:
        if self.is_imported(entity, client):
            warnings.simplefilter("always")
            warnings.warn(
                f"Experiment {entity.name} is already present in the DB. Skipping import."
            )
            return False

        if not entity.product._validator.is_imported(
            entity=entity.product, client=client
        ):
            raise ImportValidationException(
                (
                    f"Product {entity.product.code} is not present in the DB. "
                    "Please import the product first"
                )
            )

        for variable in entity.variables:
            if not variable._validator.is_imported(entity=variable, client=client):
                raise ImportValidationException(
                    (
                        f"Variable {variable.code} is not present in the DB. "
                        "Please import the variable first"
                    )
                )

        if not entity.file_data:
            raise ImportValidationException("File data is missing")

        return True

    def is_imported(self, entity: Union[Experiment, Recipe], client: Client) -> bool:
        """Check if the experiment is already imported"""

        if not entity.id:
            return False

        response = entity.requests(client).get(entity.id)

        if response:
            return True
        return False
