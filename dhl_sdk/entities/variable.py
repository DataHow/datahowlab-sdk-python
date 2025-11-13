from typing import TYPE_CHECKING, final
from typing_extensions import override

if TYPE_CHECKING:
    from dhl_sdk.client import DataHowLabClient
    from openapi_client.models.variable import Variable as OpenAPIVariable
    from openapi_client.models.variable_create import VariableCreate
    from openapi_client.models.variantdetails import Variantdetails
    from openapi_client.models.variantdetails1 import Variantdetails1


@final
class Variable:
    def __init__(self, variable: "OpenAPIVariable"):
        self._variable = variable

    @override
    def __str__(self) -> str:
        return f"Variable(code={self._variable.code}, group={self._variable.group}, measurementUnit={self._variable.measurement_unit})"

    @property
    def id(self) -> str:
        return self._variable.id

    @property
    def name(self) -> str:
        return self._variable.name

    @property
    def code(self) -> str:
        return self._variable.code

    @property
    def description(self) -> str:
        return self._variable.description

    @property
    def measurement_unit(self) -> str:
        return self._variable.measurement_unit

    @property
    def group(self) -> str:
        return self._variable.group

    @property
    def variant_details(self) -> "Variantdetails":
        return self._variable.variant_details

    @property
    def tags(self) -> dict[str, str] | None:
        return self._variable.tags


class VariableRequest:
    _variable_create: "VariableCreate"

    def __init__(self, variable_create: "VariableCreate"):
        self._variable_create = variable_create

    @override
    def __str__(self) -> str:
        return f"VariableRequest(code={self._variable_create.code}, group={self._variable_create.group}, measurementUnit={self._variable_create.measurement_unit})"

    @staticmethod
    def new(
        name: str,
        code: str,
        description: str,
        measurement_unit: str,
        group: str,
        variant_details: "Variantdetails1",
        tags: dict[str, str] | None = None,
    ) -> "VariableRequest":
        from openapi_client.models.variable_create import VariableCreate

        variable_create = VariableCreate(
            name=name,
            code=code,
            description=description,
            measurementUnit=measurement_unit,
            group=group,
            variantDetails=variant_details,
            tags=tags,
        )
        return VariableRequest(variable_create)

    def create(self, client: "DataHowLabClient") -> Variable:
        from dhl_sdk.error_handler import handle_validation_errors

        @handle_validation_errors
        def _create():
            return client.api.create_variable_api_v1_variables_post(variable_create=self._variable_create)

        created_variable = _create()
        return Variable(created_variable)
