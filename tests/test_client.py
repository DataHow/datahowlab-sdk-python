# pylint: disable=missing-docstring
import unittest
from unittest.mock import patch, Mock

from dhl_sdk.authentication import APIKeyAuthentication
from dhl_sdk.client import Client, DataHowLabClient
from dhl_sdk.crud import CRUDClient
from dhl_sdk.entities import CultivationProject


class TestGetAPIKey(unittest.TestCase):
    @patch.dict("os.environ", {"DHL_API_KEY": "test_api_key"})
    def test_get_api_key_from_environment_variable(self):
        # Test when API key is retrieved from environment variable
        auth_key = APIKeyAuthentication()
        headers = auth_key.get_headers()
        self.assertEqual(headers["Authorization"], "ApiKey test_api_key")

    @patch("os.environ.get", return_value=None)
    def test_no_api_key_provided(self, mock_env_get):
        # Test when no API key is provided
        with self.assertRaises(KeyError):
            _ = APIKeyAuthentication()


class TestClient(unittest.TestCase):
    def setUp(self):
        self.auth_key = APIKeyAuthentication("test_auth_key")
        self.base_url = "https://test.com"
        self.client = Client(self.auth_key, self.base_url)

    def test_init(self):
        self.assertEqual(self.client.auth_key, self.auth_key)

    @patch("requests.Session.post")
    def test_post(self, mock_post):
        json_data = {"test_key": "test_value"}
        self.client.post("api/test", json_data)
        mock_post.assert_called_once_with(
            "https://test.com/api/test",
            headers={"Authorization": "ApiKey test_auth_key"},
            json=json_data,
        )

    @patch("requests.Session.get")
    def test_get(self, mock_get):
        query_params = {"offset": "0", "limit": "10", "filterBy[name]": "foo%=bar"}

        self.client.get("api/test", query_params)
        mock_get.assert_called_once_with(
            "https://test.com/api/test?offset=0&limit=10&filterBy[name]=foo%25%3Dbar",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("dhl_sdk.client.Client.get")
    def test_get_projects(self, mock_get):
        offset = 0
        name = "test_name"
        unit_id = "test_unit_id"

        with self.assertRaises(StopIteration):
            # it should raise an error since there is no data
            result = self.client.get_projects(
                project_type=CultivationProject,
                offset=offset,
                name=name,
                process_unit_id=unit_id,
            )
            _ = next(result)

        mock_get.assert_called_once_with(
            "api/db/v2/projects",
            query_params={
                "offset": "0",
                "limit": "10",
                "filterBy[name]": name,
                "filterBy[processUnitId]": unit_id,
                "archived": "false",
                "sortBy[createdAt]": "desc",
            },
        )

    @patch("dhl_sdk.client.Client.get")
    def test_get_products(self, mock_get):
        client = DataHowLabClient(self.auth_key, self.base_url)
        code = "TESTCODE"

        with self.assertRaises(StopIteration):
            # it should raise an error since there is no data
            result = client.get_products(code=code)
            _ = next(result)

        mock_get.assert_called_once_with(
            "api/db/v2/products",
            query_params={
                "offset": "0",
                "limit": "10",
                "filterBy[code]": code,
                "archived": "false",
                "sortBy[createdAt]": "desc",
            },
        )

    @patch("dhl_sdk.client.Client.get")
    def test_get_recipes(self, mock_get):
        client = DataHowLabClient(self.auth_key, self.base_url)
        name = "test name"
        product = Mock(
            id="test_product_id",
            code="test_product_code",
            name="test_product_name",
        )

        with self.assertRaises(StopIteration):
            # it should raise an error since there is no data
            result = client.get_recipes(name=name, product=product)
            _ = next(result)

        mock_get.assert_called_once_with(
            "api/db/v2/recipes",
            query_params={
                "offset": "0",
                "limit": "10",
                "filterBy[name]": name,
                "filterBy[product._id]": product.id,
                "archived": "false",
                "sortBy[createdAt]": "desc",
            },
        )

    @patch("dhl_sdk.client.Client.get")
    def test_get_experiments(self, mock_get):
        client = DataHowLabClient(self.auth_key, self.base_url)
        name = "test name"
        product = Mock(
            id="test_product_id",
            code="test_product_code",
            name="test_product_name",
        )

        with self.assertRaises(StopIteration):
            # it should raise an error since there is no data
            result = client.get_experiments(name=name, product=product)
            _ = next(result)

        mock_get.assert_called_once_with(
            "api/db/v2/experiments",
            query_params={
                "offset": "0",
                "limit": "10",
                "search": "test name",
                "filterBy[product._id]": product.id,
                "archived": "false",
                "sortBy[createdAt]": "desc",
            },
        )

    @patch("dhl_sdk.client.Client.get")
    def test_get_experiments_noproduct(self, mock_get):
        client = DataHowLabClient(self.auth_key, self.base_url)
        name = "test name"

        with self.assertRaises(StopIteration):
            # it should raise an error since there is no data
            result = client.get_experiments(name=name)
            _ = next(result)

        mock_get.assert_called_once_with(
            "api/db/v2/experiments",
            query_params={
                "offset": "0",
                "limit": "10",
                "search": "test name",
                "archived": "false",
                "sortBy[createdAt]": "desc",
            },
        )

    @patch("dhl_sdk.client.Client.get")
    def test_get_variables(self, mock_get):
        client = DataHowLabClient(self.auth_key, self.base_url)
        code = "TESTCODE"
        variable_type = "categorical"
        group = "X Variables"

        mock_variable_group_codes = Mock()
        mock_variable_group_codes.get_variable_group_codes.return_value = {
            "X Variables": ("959606c1-44bc-4657-82ff-70c247be14aa", "X")
        }

        with patch(
            "dhl_sdk.client.VariableGroupCodes", return_value=mock_variable_group_codes
        ):
            with self.assertRaises(ValueError):
                # it should raise an error since variable_type is not valid
                result = client.get_variables(
                    code=code, variable_type="test", group=group
                )

            with self.assertRaises(ValueError):
                # it should raise an error since group is not valid
                result = client.get_variables(
                    code=code, variable_type=variable_type, group="test"
                )

            with self.assertRaises(StopIteration):
                # it should raise an error since there is no data
                result = client.get_variables(
                    code=code, variable_type=variable_type, group=group
                )
                _ = next(result)

            mock_get.assert_called_once_with(
                "api/db/v2/variables",
                query_params={
                    "offset": "0",
                    "limit": "10",
                    "filterBy[code]": code,
                    "filterBy[variant]": variable_type,
                    "filterBy[group._id]": "959606c1-44bc-4657-82ff-70c247be14aa",
                    "archived": "false",
                    "sortBy[createdAt]": "desc",
                },
            )
