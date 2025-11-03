from collections.abc import Iterator
from typing import TYPE_CHECKING, final
from typing_extensions import override

from dhl_sdk._utils import paginate

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.project import Project as OpenAPIProject
    from openapi_client.models.model import Model as OpenAPIModel


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

    # FIXME missing
    # @property
    #   def tags(self) -> dict[str, str]:
    #    return self._project.tags or {}

    def get_models(self) -> "Iterator[OpenAPIModel]":
        return paginate(
            self._api.get_models_api_v1_projects_project_id_models_get,
            project_id=self._project.id,
        )
