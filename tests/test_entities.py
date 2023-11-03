import unittest
from unittest.mock import Mock
from unittest.mock import patch

from dhl_sdk.authentication import APIKeyAuthentication
from dhl_sdk.client import Client

from dhl_sdk.crud import Result
from dhl_sdk.entities import Model, Project, Variable


class TestProjectEntity(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.get.return_value = Mock(
            json=lambda: [
                {
                    "id": "id-123",
                    "name": "project 1",
                    "description": "description 1",
                    "processUnitId": "unit1",
                },
                {
                    "id": "id-456",
                    "name": "project 2",
                    "description": "description 2",
                    "processUnitId": "Unit1",
                },
            ],
            headers={"x-total-count": "2"},
        )

    def test_projects_list(self):
        projects, total = Project.requests(self.client).list(0, 10)

        self.assertEqual(total, 2)
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0].id, "id-123")
        self.assertEqual(projects[0].name, "project 1")
        self.assertEqual(projects[1].process_unit_id, "Unit1")

    def test_projects_result(self):
        project_requests = Project.requests(self.client)
        result = Result[Project](0, 5, {}, project_requests)

        p1 = next(result)

        self.assertEqual(p1.id, "id-123")
        self.assertEqual(p1.name, "project 1")

        p2 = next(result)

        self.assertEqual(p2.id, "id-456")
        self.assertEqual(p2.name, "project 2")

    def test_projects_get_models(self):
        project_requests = Project.requests(self.client)
        result = Result[Project](0, 5, {}, project_requests)
        project = next(result)

        models = project.get_models()
        self.assertTrue(isinstance(models, Result))


class TestVariableEntity(unittest.TestCase):
    def test_variable_spectrum(self):
        client = Mock()
        client.get.return_value = Mock(
            json=lambda: {
                "id": "var-id-123",
                "name": "Variable 1",
                "code": "var1",
                "variant": "spectrum",
                "spectrum": {"xAxis": {"dimension": 10}},
            }
        )

        request = Variable.requests(client)

        var = request.get("var-id-123")

        self.assertEqual(var.id, "var-id-123")
        self.assertEqual(var.name, "Variable 1")
        self.assertEqual(var.size, 10)

    def test_variable_numeric(self):
        client = Mock()
        client.get.return_value = Mock(
            json=lambda: {
                "id": "var-id-123",
                "name": "Variable 1",
                "code": "var1",
                "variant": "numeric",
            }
        )

        request = Variable.requests(client)
        var = request.get("var-id-123")

        self.assertEqual(var.id, "var-id-123")
        self.assertEqual(var.name, "Variable 1")
        self.assertTrue(var.size is None)


class TestEntitiesRequests(unittest.TestCase):
    def setUp(self):
        self.auth_key = APIKeyAuthentication("test_auth_key")
        self.base_url = "https://test.com"
        self.client = Client(self.auth_key, self.base_url)

    @patch("requests.Session.get")
    def test_get_variables(self, mock_get):
        request = Variable.requests(self.client)

        with self.assertRaises(KeyError):
            var = request.get("var-id-123")

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/variables/var-id-123",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    def test_get_projects_result(self, mock_get):
        project_requests = Project.requests(self.client)
        result = Result[Project](0, 5, {}, project_requests)
        with self.assertRaises(StopIteration):
            next(result)

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/projects?offset=0&limit=5&archived=false&sortBy[createdAt]=desc",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    def test_get_models_result(self, mock_get):
        model_requests = Model.requests(self.client)
        result = Result[Model](0, 5, {}, model_requests)

        with self.assertRaises(StopIteration):
            next(result)

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/pipelineJobs?offset=0&limit=5&archived=false&sortBy[createdAt]=desc",
            headers={"Authorization": "ApiKey test_auth_key"},
        )
