# Disable import cycle check: Project and Model have bidirectional references through ModelExperiment/Product
# (those are only relevant for type checking)
# pyright: reportImportCycles=false
from collections.abc import Iterator
from typing import TYPE_CHECKING, final
from typing_extensions import override

from dhl_sdk._utils import paginate
from dhl_sdk import convert_tags_for_openapi

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.model_type import ModelType
    from openapi_client.models.project import Project as OpenAPIProject
    from dhl_sdk.entities.model import Model


@final
class Project:
    def __init__(self, project: "OpenAPIProject", api: "DefaultApi"):
        self._project = project
        self._api = api

    @override
    def __str__(self) -> str:
        return f"Project(name={self._project.name})"

    @property
    def id(self) -> str:
        return self._project.id

    @property
    def name(self) -> str:
        return self._project.name

    @property
    def description(self) -> str:
        return self._project.description

    @property
    def process_unit(self):
        return self._project.process_unit

    @property
    def process_format(self):
        return self._project.process_format

    @property
    def tags(self) -> dict[str, str]:
        return self._project.tags or {}

    def get_models(
        self,
        search: str | None = None,
        name: str | None = None,
        tags: dict[str, str] | None = None,
        model_type: "ModelType | list[ModelType] | None" = None,
    ) -> "Iterator[Model]":
        """
        Get all models in this project.

        Parameters
        ----------
        search : str, optional
            Free-text search to filter models.
        name : str, optional
            Filter by model name (exact match).
        tags : dict[str, str], optional
            Filter by tags using key-value pairs (e.g., {"manufacturer": "example", "location": "plant1"}).
        model_type : ModelType | list[ModelType], optional
            The model type(s) to filter by (e.g., ModelType.PROPAGATION).
            Available values: PROPAGATION, HISTORICAL, COMBINED.
            Can be a single value or list.

        Returns
        -------
        Iterator
            Iterator of Model instances
        """
        from dhl_sdk.entities.model import Model

        model_type_list: list[ModelType] | None = None
        if isinstance(model_type, list):
            model_type_list = model_type
        elif model_type is not None:
            model_type_list = [model_type]

        # Convert tags to OpenAPI format (dict[str, str] -> dict[str, dict[str, str]])
        tags_openapi = convert_tags_for_openapi(tags)

        for api_model in paginate(
            self._api.get_models_api_v1_projects_project_id_models_get,
            project_id=self._project.id,
            search=search,
            name=name,
            tags=tags_openapi,
            model_type=model_type_list,
        ):
            yield Model(api_model, self._api)
