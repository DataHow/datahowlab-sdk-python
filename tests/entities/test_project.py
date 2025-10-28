import unittest
from unittest.mock import Mock
from typing import TYPE_CHECKING

from openapi_client.models.project import Project as OpenAPIProject

from dhl_sdk.entities.project import Project
from tests.entities._fixtures import create_model, create_project

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi


class TestProject(unittest.TestCase):
    api_project: OpenAPIProject
    mock_api: "DefaultApi"

    def setUp(self):
        self.api_project = create_project(id="proj-123", name="Test Project", description="A test project")
        self.mock_api = Mock()

    def test_init(self):
        project = Project(self.api_project, self.mock_api)
        self.assertIsNotNone(project)

    def test_str(self):
        project = Project(self.api_project, self.mock_api)
        result = str(project)
        self.assertEqual(result, "Project(name=Test Project)")

    def test_id_property(self):
        project = Project(self.api_project, self.mock_api)
        self.assertEqual(project.id, "proj-123")

    def test_name_property(self):
        project = Project(self.api_project, self.mock_api)
        self.assertEqual(project.name, "Test Project")

    def test_description_property(self):
        project = Project(self.api_project, self.mock_api)
        self.assertEqual(project.description, "A test project")

    def test_process_unit_property(self):
        project = Project(self.api_project, self.mock_api)
        self.assertIsNotNone(project.process_unit)

    def test_process_format_property(self):
        project = Project(self.api_project, self.mock_api)
        self.assertIsNotNone(project.process_format)

    def test_get_models_empty(self):
        self.mock_api.get_models_api_v1_projects_project_id_models_get.return_value = []
        project = Project(self.api_project, self.mock_api)

        models = list(project.get_models())

        self.assertEqual(len(models), 0)
        self.mock_api.get_models_api_v1_projects_project_id_models_get.assert_called_once_with(project_id="proj-123", skip=0, limit=10)

    def test_get_models_with_results(self):
        mock_model1 = create_model(name="Test Model 1")
        mock_model2 = create_model(name="Test Model 2")

        self.mock_api.get_models_api_v1_projects_project_id_models_get.return_value = [mock_model1, mock_model2]
        project = Project(self.api_project, self.mock_api)

        models = list(project.get_models())

        self.assertEqual(len(models), 2)
        self.assertEqual(models[0].id, mock_model1.id)
        self.assertEqual(models[1].id, mock_model2.id)

    def test_get_models_pagination(self):
        mock_models_page1 = [create_model(name=f"Test Model {i}") for i in range(10)]
        mock_models_page2 = [create_model(name=f"Test Model {i + 10}") for i in range(5)]

        self.mock_api.get_models_api_v1_projects_project_id_models_get.side_effect = [
            mock_models_page1,
            mock_models_page2,
        ]
        project = Project(self.api_project, self.mock_api)

        models = list(project.get_models())

        self.assertEqual(len(models), 15)
        self.assertEqual(self.mock_api.get_models_api_v1_projects_project_id_models_get.call_count, 2)
