# pylint: disable=missing-docstring
import unittest
from unittest.mock import Mock, patch

from dhl_sdk.authentication import APIKeyAuthentication
from dhl_sdk.client import Client, DataHowLabClient
from dhl_sdk.crud import Result
from dhl_sdk.entities import (
    CultivationHistoricalModel,
    CultivationProject,
    CultivationPropagationModel,
    ModelFactory,
    SpectraModel,
    Variable,
)


class TestProjectEntity(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.get.return_value = Mock(
            json=lambda: [
                {
                    "id": "id-123",
                    "name": "project 1",
                    "description": "description 1",
                    "processUnitId": "373c173a-1f23-4e56-874e-90ca4702ec0d",
                },
                {
                    "id": "id-456",
                    "name": "project 2",
                    "description": "description 2",
                    "processUnitId": "373c173a-1f23-4e56-874e-90ca4702ec0d",
                },
            ],
            headers={"x-total-count": "2"},
        )

    def test_projects_list(self):
        projects, total = CultivationProject.requests(self.client).list(0, 10)

        self.assertEqual(total, 2)
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0].id, "id-123")
        self.assertEqual(projects[0].name, "project 1")
        self.assertEqual(
            projects[1].process_unit_id, "373c173a-1f23-4e56-874e-90ca4702ec0d"
        )

    def test_projects_result(self):
        project_requests = CultivationProject.requests(self.client)
        result = Result[CultivationProject](5, {}, project_requests)

        p1 = next(result)

        self.assertEqual(p1.id, "id-123")
        self.assertEqual(p1.name, "project 1")

        p2 = next(result)

        self.assertEqual(p2.id, "id-456")
        self.assertEqual(p2.name, "project 2")

    def test_projects_get_models(self):
        project_requests = CultivationProject.requests(self.client)
        result = Result[CultivationProject](5, {}, project_requests)
        project = next(result)

        models = project.get_models()
        self.assertTrue(isinstance(models, Result))

    def test_model_factory(self):
        model_factory = ModelFactory("373c173a-1f23-4e56-874e-90ca4702ec0d")
        model = model_factory.get_model()

        self.assertEqual(model, SpectraModel)

        model_factory = ModelFactory("04a324da-13a5-470b-94a1-bda6ac87bb86")
        model = model_factory.get_model(model_type="propagation")
        self.assertEqual(model, CultivationPropagationModel)

        model_factory = ModelFactory("04a324da-13a5-470b-94a1-bda6ac87bb86")
        model = model_factory.get_model(model_type="historical")
        self.assertEqual(model, CultivationHistoricalModel)

        model_factory = ModelFactory("04a324da-13a5-470b-94a1-bda6ac871234")
        with self.assertRaises(NotImplementedError):
            model_factory.get_model()


class TestEntitiesRequests(unittest.TestCase):
    def setUp(self):
        self.auth_key = APIKeyAuthentication("test_auth_key")
        self.base_url = "https://test.com"
        self.client = Client(self.auth_key, self.base_url)

    @patch("requests.Session.get")
    def test_get_variables(self, mock_get):
        request = Variable.requests(self.client)

        with self.assertRaises(KeyError):
            _ = request.get("var-id-123")

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/variables/var-id-123",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    def test_get_projects_result(self, mock_get):
        project_requests = CultivationProject.requests(self.client)
        result = Result[CultivationProject](5, {}, project_requests)
        with self.assertRaises(StopIteration):
            next(result)

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/projects?offset=0"
            "&limit=5&archived=false&sortBy[createdAt]=desc",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    def test_get_spectramodels_result(self, mock_get):
        model_requests = SpectraModel.requests(self.client)
        result = Result[SpectraModel](5, {}, model_requests)

        with self.assertRaises(StopIteration):
            next(result)

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/pipelineJobs?offset=0"
            "&limit=5&archived=false&sortBy[createdAt]=desc",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    def test_get_cultivationmodels_result(self, mock_get):
        model_requests = CultivationPropagationModel.requests(self.client)
        result = Result[CultivationPropagationModel](5, {}, model_requests)

        with self.assertRaises(StopIteration):
            next(result)

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/pipelineJobs?offset=0"
            "&limit=5&archived=false&sortBy[createdAt]=desc",
            headers={"Authorization": "ApiKey test_auth_key"},
        )
