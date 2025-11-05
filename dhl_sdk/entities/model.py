# Disable import cycle check: Model and ModelExperiment have bidirectional references
# (Model creates ModelExperiment, ModelExperiment holds Model)
# pyright: reportImportCycles=false
from collections.abc import Iterator
from typing import TYPE_CHECKING
from typing_extensions import override

from dhl_sdk._utils import paginate

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.model import Model as OpenAPIModel
    from dhl_sdk.entities.model_variable import ModelVariable
    from dhl_sdk.entities.model_experiment import ModelExperiment


class Model:
    _model: "OpenAPIModel"

    def __init__(self, model: "OpenAPIModel"):
        self._model = model

    @override
    def __str__(self) -> str:
        return f"Model({self.name}, {self.type})"

    @property
    def id(self) -> str:
        return self._model.id

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def description(self) -> str:
        return self._model.description

    @property
    def status(self) -> str:
        return self._model.status.value

    @property
    def type(self) -> str:
        return self._model.type.value

    @property
    def project_id(self) -> str:
        return self._model.project_id

    @property
    def dataset_id(self) -> str | None:
        return self._model.dataset_id

    @property
    def variant(self) -> str:
        return self._model.variant

    @property
    def step_size(self) -> int | None:
        return self._model.step_size

    @property
    def success(self) -> bool:
        """Returns True if model status is 'success'."""
        return self.status == "success"

    def get_variables(self, api: "DefaultApi") -> "Iterator[ModelVariable]":
        """
        Get all variables associated with this model.

        Returns:
            Iterator of ModelVariable objects used in this model
        """
        from dhl_sdk.entities.model_variable import ModelVariable

        for api_model_variable in paginate(
            api.get_model_variables_api_v1_models_model_id_variables_get,
            model_id=self.id,
        ):
            yield ModelVariable(api_model_variable)

    def get_experiments(self, api: "DefaultApi") -> "Iterator[ModelExperiment]":
        """
        Get all experiments used in this model.

        Returns:
            Iterator of ModelExperiment objects used in this model
        """
        from dhl_sdk.entities.model_experiment import ModelExperiment  # type: ignore[attr-defined]

        for api_model_experiment in paginate(
            api.get_model_experiments_api_v1_models_model_id_experiments_get,
            model_id=self.id,
        ):
            yield ModelExperiment(api_model_experiment, self)
