from typing import TYPE_CHECKING, final
from typing_extensions import override

if TYPE_CHECKING:
    from openapi_client.models.group import Group as OpenAPIGroup
    from openapi_client.models.variable_variant import VariableVariant


@final
class VariableGroup:
    """
    Wrapper for OpenAPI Group entity (Variable Groups).

    Variable groups represent collections of related variables with consistent
    variants across process units and formats.
    """

    def __init__(self, group: "OpenAPIGroup"):
        self._group = group

    @override
    def __str__(self) -> str:
        return f"VariableGroup(name={self._group.name}, code={self._group.code})"

    @property
    def id(self) -> str:
        """Unique identifier for the variable group."""
        return self._group.id

    @property
    def name(self) -> str:
        """Name of the variable group."""
        return self._group.name

    @property
    def code(self) -> str:
        """Code identifier for the variable group."""
        return self._group.code

    @property
    def description(self) -> str:
        """Description of the variable group."""
        return self._group.description

    @property
    def tags(self) -> dict[str, str]:
        """
        Tags associated with the variable group.

        Returns
        -------
        dict[str, str]
            Dictionary of tag key-value pairs. Returns empty dict if no tags.
        """
        return self._group.tags or {}

    @property
    def variable_variants(self) -> "list[VariableVariant] | None":
        """
        Available variable variants for this group.

        Returns
        -------
        list[VariableVariant] | None
            List of variable variants (e.g., NUMERIC, CATEGORICAL, LOGICAL, SPECTRUM, FLOW)
            or None if not specified.
        """
        return self._group.variable_variants
