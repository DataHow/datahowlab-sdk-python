from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.variable import Variable as OpenAPIVariable
    from openapi_client.models.variable_create import VariableCreate


class Variable:
    def __init__(self, variable: "OpenAPIVariable"):
        self._variable = variable

    def __str__(self) -> str:
        group = self._variable.group or ""
        unit = self._variable.measurement_unit or ""
        return f"Variable(code={self._variable.code}, group={group}, measurementUnit={unit})"

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
    def description(self) -> str | None:
        return self._variable.description

    @property
    def measurement_unit(self) -> str | None:
        return self._variable.measurement_unit

    @property
    def group(self) -> str | None:
        return self._variable.group

    @property
    def variant_details(self) -> Any:
        return self._variable.variant_details

    @property
    def tags(self) -> dict[str, Any] | None:
        return self._variable.tags


class VariableRequest:
    def __init__(self, variable_create: "VariableCreate"):
        self._variable_create = variable_create

    def __str__(self) -> str:
        group = self._variable_create.group or ""
        unit = self._variable_create.measurement_unit or ""
        return f"VariableRequest(code={self._variable_create.code}, group={group}, measurementUnit={unit})"

    @staticmethod
    def new(
        name: str,
        code: str,
        description: str,
        measurement_unit: str,
        group: str,
        variant_details: Any,
        tags: dict[str, Any] | None = None,
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

    def create(self, api: "DefaultApi") -> Variable:
        from openapi_client.models.variable import Variable as OpenAPIVariable

        created_variable: OpenAPIVariable = api.create_variable_api_v1_variables_post(variable_create=self._variable_create)
        return Variable(created_variable)
