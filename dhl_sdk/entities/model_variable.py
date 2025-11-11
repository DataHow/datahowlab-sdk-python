from typing import TYPE_CHECKING
from typing_extensions import override

if TYPE_CHECKING:
    from openapi_client.models.model_variable import ModelVariable as OpenAPIModelVariable


class ModelVariable:
    _model_variable: "OpenAPIModelVariable"

    def __init__(self, model_variable: "OpenAPIModelVariable"):
        self._model_variable = model_variable

    @override
    def __str__(self) -> str:
        return f"ModelVariable({self.code}, {self.group}, {self.measurement_unit})"

    @property
    def id(self) -> str:
        return self._model_variable.id

    @property
    def name(self) -> str:
        return self._model_variable.name

    @property
    def code(self) -> str:
        return self._model_variable.code

    @property
    def description(self) -> str:
        return self._model_variable.description

    @property
    def measurement_unit(self) -> str:
        return self._model_variable.measurement_unit

    @property
    def group(self) -> str:
        return self._model_variable.group

    @property
    def variant(self) -> str:
        return self._model_variable.variant.value

    @property
    def input_type(self) -> str:
        return self._model_variable.input_type.value

    @property
    def output_type(self) -> str:
        return self._model_variable.output_type.value

    @property
    def disposition(self) -> str:
        return self._model_variable.disposition
