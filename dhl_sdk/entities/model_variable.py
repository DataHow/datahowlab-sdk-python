from typing import TYPE_CHECKING, final
from typing_extensions import override

if TYPE_CHECKING:
    from openapi_client.models.model_variable import ModelVariable as OpenAPIModelVariable
    from openapi_client.models.variantdetails1 import Variantdetails1


@final
class ModelVariable:
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
    def variant_details(self) -> "Variantdetails1":
        return self._model_variable.variant_details

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
    def aggregation(self) -> str:
        return self._model_variable.aggregation.value

    @property
    def input_type(self) -> str:
        return self._model_variable.input_type.value

    @property
    def output_type(self) -> str:
        return self._model_variable.output_type.value

    @property
    def disposition(self) -> str:
        return self._model_variable.disposition

    @property
    def tags(self) -> dict[str, str]:
        """
        Tags associated with the model variable.

        Returns
        -------
        dict[str, str]
            Dictionary of tag key-value pairs. Returns empty dict if no tags.
        """
        return self._model_variable.tags or {}
