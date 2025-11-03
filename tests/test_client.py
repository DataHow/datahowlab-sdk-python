import unittest
from unittest.mock import patch, Mock

from dhl_sdk.authentication import APIKeyAuthentication
from dhl_sdk.client import DataHowLabClient


class TestGetAPIKey(unittest.TestCase):
    @patch.dict("os.environ", {"DHL_API_KEY": "test_api_key"})
    def test_get_api_key_from_environment_variable(self):
        auth_key = APIKeyAuthentication()
        headers = auth_key.get_headers()
        self.assertEqual(headers["Authorization"], "ApiKey test_api_key")

    @patch("os.environ.get", return_value=None)
    def test_no_api_key_provided(self, mock_env_get):
        with self.assertRaises(KeyError):
            _ = APIKeyAuthentication()


class TestDataHowLabClient(unittest.TestCase):
    auth_key: APIKeyAuthentication
    base_url: str

    def setUp(self):
        self.auth_key = APIKeyAuthentication("test_auth_key")
        self.base_url = "https://test.com"

    @patch("openapi_client.api.default_api.DefaultApi.get_projects_api_v1_projects_get")
    def test_get_projects(self, mock_get_projects):
        client = DataHowLabClient(self.auth_key, self.base_url)

        mock_get_projects.return_value = []

        result = list(client.get_projects())

        self.assertEqual(len(result), 0)
        mock_get_projects.assert_called_once_with(skip=0, limit=10, search=None, process_unit=None, process_format=None)

    @patch("openapi_client.api.default_api.DefaultApi.get_projects_api_v1_projects_get")
    def test_get_projects_with_filters(self, mock_get_projects):
        from openapi_client.models.process_unit_code import ProcessUnitCode

        client = DataHowLabClient(self.auth_key, self.base_url)

        mock_project = Mock()
        mock_project.name = "Test Project"
        mock_get_projects.return_value = [mock_project]

        result = list(client.get_projects(search="Test Project", process_unit=ProcessUnitCode.BR))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Test Project")
        mock_get_projects.assert_called_once_with(
            skip=0, limit=10, search="Test Project", process_unit=[ProcessUnitCode.BR], process_format=None
        )

    @patch("openapi_client.api.default_api.DefaultApi.get_products_api_v1_products_get")
    def test_get_products(self, mock_get_products):
        client = DataHowLabClient(self.auth_key, self.base_url)

        mock_product = Mock()
        mock_product.code = "TESTCODE"
        mock_get_products.return_value = [mock_product]

        result = list(client.get_products())

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].code, "TESTCODE")
        mock_get_products.assert_called_once_with(skip=0, limit=10, search=None, process_format=None)

    @patch("openapi_client.api.default_api.DefaultApi.get_experiments_api_v1_experiments_get")
    def test_get_experiments(self, mock_get_experiments):
        client = DataHowLabClient(self.auth_key, self.base_url)

        mock_experiment = Mock()
        mock_experiment.id = "test-experiment-id"
        mock_get_experiments.return_value = [mock_experiment]

        result = list(client.get_experiments(search="Test"))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "test-experiment-id")
        mock_get_experiments.assert_called_once_with(skip=0, limit=10, search="Test", process_unit=None, process_format=None)

    @patch("openapi_client.api.default_api.DefaultApi.get_variables_api_v1_variables_get")
    def test_get_variables(self, mock_get_variables):
        client = DataHowLabClient(self.auth_key, self.base_url)

        mock_variable = Mock()
        mock_variable.code = "VAR1"
        mock_get_variables.return_value = [mock_variable]

        result = list(client.get_variables())

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].code, "VAR1")
        mock_get_variables.assert_called_once_with(skip=0, limit=10, search=None)

    @patch("openapi_client.api.default_api.DefaultApi.get_projects_api_v1_projects_get")
    def test_pagination(self, mock_get_projects):
        client = DataHowLabClient(self.auth_key, self.base_url)

        mock_page1 = [Mock(id=f"proj-{i}") for i in range(10)]
        mock_page2 = [Mock(id=f"proj-{i}") for i in range(10, 15)]

        mock_get_projects.side_effect = [mock_page1, mock_page2]

        result = list(client.get_projects())

        self.assertEqual(len(result), 15)
        self.assertEqual(mock_get_projects.call_count, 2)
        mock_get_projects.assert_any_call(skip=0, limit=10, search=None, process_unit=None, process_format=None)
        mock_get_projects.assert_any_call(skip=10, limit=10, search=None, process_unit=None, process_format=None)
