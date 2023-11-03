# pylint: disable=no-member
# pylint: disable=unsubscriptable-object
"""API Entities Module

This module provides a comprehensive set of Pydantic models that represent
multiple entities obtained from the API . 

Classes:
    - Variable: Represents a structure for variables present in the models.
    - Dataset: Represents a structure for datasets present in the models.
    - Model: Represents a structure for models fetched from the API.
    - Project: Represents a structure for projects retrieved from the API.
"""
from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from dhl_sdk.crud import Result, Client, CRUDClient
from dhl_sdk.exceptions import ModelPredictionException
from dhl_sdk._utils import PredictResponse
from dhl_sdk._spectra_utils import (
    SpectraData,
    SpectraPrediction,
    convert_to_request,
    format_predictions,
    validate_prediction_inputs,
)

PROJECTS_URL = "api/db/v2/projects"
DATASETS_URL = "api/db/v2/datasets"
VARIABLES_URL = "api/db/v2/variables"
MODELS_URL = "api/db/v2/pipelineJobs"


class Variable(BaseModel):
    """Model Variable"""

    id: str = Field(alias="id")
    name: str = Field(alias="name")
    code: str = Field(alias="code")
    variant: str = Field(alias="variant")
    size: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def _validate_size(cls, data) -> dict:
        if data["variant"] == "spectrum":
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

    @staticmethod
    def requests(client: Client) -> CRUDClient["Variable"]:
        return CRUDClient["Variable"](client, VARIABLES_URL, Variable)


class Dataset(BaseModel):
    """Model Dataset"""

    id: str = Field(alias="id")
    variables: list[Variable] = Field(alias="variables")
    _client: Client = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._client = data["client"]

    @model_validator(mode="before")
    @classmethod
    def _validate_variables(cls, data) -> dict:
        unpacked_variables = []

        for i, variable_info in enumerate(data["variables"]):
            try:
                var_id = variable_info["id"]
            except KeyError as err:
                raise KeyError(
                    f"The variable at index {i} does not contain an id"
                ) from err

            var = Variable.requests(data["client"]).get(var_id)
            unpacked_variables.append(var)

        data["variables"] = unpacked_variables

        return data

    def get_spectrum_index(self) -> int:
        """Get the index of the spectrum variable"""
        for index, variable in enumerate(self.variables):
            if variable.variant == "spectrum":
                return index
        raise ValueError("No spectrum variable found in dataset")

    @staticmethod
    def requests(client: Client) -> CRUDClient["Dataset"]:
        return CRUDClient["Dataset"](client, DATASETS_URL, Dataset)


class Model(BaseModel):
    """Pydantic Model for Prediction Model from the API"""

    id: str = Field(alias="id")
    name: str = Field(alias="name")
    status: str = Field(alias="status")
    config: dict = Field(alias="config")
    dataset: Dataset = Field(alias="dataset")
    project_id: str = Field(alias="projectId")
    _client: Client = PrivateAttr()
    _spectra_size: Optional[int] = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self._client = data["client"]

    @model_validator(mode="before")
    @classmethod
    def _validate_model_data(cls, data) -> dict:
        data["dataset"] = Dataset(**data["dataset"], client=data["client"])
        return data

    def predict(
        self,
        spectra: SpectraData,
        inputs: Optional[dict] = None,
    ) -> SpectraPrediction:
        """
        Predicts the output of a given model for a given set of spectra.

        Parameters:
        -----------
        spectra : list[list[float]] or np.ndarray
            A 2D array representing spectra for prediction, where:
                - The first dimension corresponds to the spectra index.
                - The second dimension contains wavelength index.
        inputs : dict, optional
            Additional inputs to be used for prediction. The keys must be the Codes of the
            input variables, and the values must be lists of the same length as the number
            of spectrum, by default None.

        Returns:
        --------
        Dictionary with predictions where:
            key: variable code
            value: list with predictions for each spectrum

        Example:
        --------
        >>> spectra = [[1.0, 2.0, 3.0, 3.0, 4.0, 3.0], [2.0, 3.0, 4.0, 4.0, 5.0, 4.0]]
        >>> inputs = {"input1": [42, 33]}
        >>> result = model.predict(spectra, inputs)
        >>> print(result)
        {'output1': [prediction1, prediction2], 'output2': [prediction1, prediction2]}

        """

        if not self.success:
            raise ModelPredictionException(
                f"{self.name} is not ready for prediction. The current status is {self.status}"
            )

        spectra, inputs = validate_prediction_inputs(
            spectra=spectra, model=self, inputs=inputs
        )
        json_data = convert_to_request(spectra=spectra, model=self, inputs=inputs)

        predict_url = f"api/pipeline/v1/predictors/{self.id}/predict"

        predictions = []
        for prediction_data in json_data:
            try:
                response = self._client.post(predict_url, prediction_data)
                response.raise_for_status()

                # in case of an error in the response (not HTTP)
                if "error" in response.json():
                    raise ValueError(response.json()["error"])

            except Exception as ex:
                raise ex

            predictions.append(PredictResponse(**response.json()))

        return format_predictions(predictions, model=self)

    @property
    def inputs(self) -> list[str]:
        """Get the inputs from the model's config"""
        return self.config["groups"]["Inputs"]

    @property
    def outputs(self) -> list[str]:
        """Get the outputs from the model's config"""
        return self.config["groups"]["Outputs"]

    @property
    def success(self) -> bool:
        """Get the success status of the model"""
        return self.status == "success"

    @property
    def spectra_size(self) -> int:
        """Get the size of the spectra"""
        if self._spectra_size is None:
            self._spectra_size = self._get_spectra_size()
        return self._spectra_size

    def _get_spectra_size(self) -> int:
        """Get the size of the spectra from variable information in the API"""
        spectrum = self.dataset.variables[self.dataset.get_spectrum_index()]
        return spectrum.size

    @staticmethod
    def requests(client: Client) -> CRUDClient["Model"]:
        return CRUDClient["Model"](client, MODELS_URL, Model)


class Project(BaseModel):
    """Pydantic Model for a DHL Project from the API"""

    id: str = Field(alias="id")
    name: str = Field(alias="name")
    description: str = Field(alias="description")
    process_unit_id: str = Field(alias="processUnitId")
    _client: Client = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._client = data["client"]

    def get_models(self, offset: int = 0, name: Optional[str] = None) -> Result[Model]:
        """Get the models of the project from the API"""

        models = Model.requests(self._client)

        query_params = {"filterBy[projectId]": self.id}
        if name is not None:
            query_params.update({"filterBy[name]": name})

        results = Result[Model](
            offset=offset,
            limit=5,
            query_params=query_params,
            requests=models,
        )
        return results

    @staticmethod
    def requests(client: Client) -> CRUDClient["Project"]:
        return CRUDClient["Project"](client, PROJECTS_URL, Project)
