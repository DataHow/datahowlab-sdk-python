from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.project import Project as OpenAPIProject
    from openapi_client.models.model import Model as OpenAPIModel


class Project:
    def __init__(self, project: "OpenAPIProject", api: "DefaultApi"):
        self._project = project
        self._api = api

    def __str__(self) -> str:
        return f"Project(name={self._project.name})"

    @property
    def id(self) -> str:
        return self._project.id

    @property
    def name(self) -> str:
        return self._project.name

    @property
    def description(self) -> str | None:
        return self._project.description

    @property
    def process_unit(self):
        return self._project.process_unit

    @property
    def process_format(self):
        return self._project.process_format

    def get_models(self) -> "Iterator[OpenAPIModel]":
        skip = 0
        limit = 10

        while True:
            models = self._api.get_models_api_v1_projects_project_id_models_get(
                project_id=self._project.id,
                skip=skip,
                limit=limit,
            )

            if not models:
                break

            for model in models:
                yield model

            if len(models) < limit:
                break

            skip += limit
