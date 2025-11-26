from typing import TYPE_CHECKING, final
from typing_extensions import override

if TYPE_CHECKING:
    from dhl_sdk.client import DataHowLabClient
    from openapi_client.models.variable import Variable as OpenAPIVariable
    from openapi_client.models.variable_create import VariableCreate
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
    def variant_details(self) -> "Variantdetails1":
        return self._variable.variant_details

    @property
    def variant(self) -> str:
        """Extract variant type string from variant_details for backward compatibility."""
        from openapi_client.models.numeric_details import NumericDetails
        from openapi_client.models.categorical_details import CategoricalDetails
        from openapi_client.models.logical_details import LogicalDetails
        from openapi_client.models.flow_details import FlowDetails
        from openapi_client.models.spectrum_details import SpectrumDetails

        actual = self.variant_details.actual_instance
        if isinstance(actual, NumericDetails):
            return "numeric"
        elif isinstance(actual, CategoricalDetails):
            return "categorical"
        elif isinstance(actual, LogicalDetails):
            return "logical"
        elif isinstance(actual, FlowDetails):
            return "flow"
        elif isinstance(actual, SpectrumDetails):
            return "spectrum"
        else:
            return "unknown"

    @property
    def tags(self) -> dict[str, str]:
        """
        Tags associated with the variable.

        Returns
        -------
        dict[str, str]
            Dictionary of tag key-value pairs. Returns empty dict if no tags.
        """
        return self._variable.tags or {}

    @property
    def aggregation(self) -> str:
        return self._variable.aggregation.value


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
