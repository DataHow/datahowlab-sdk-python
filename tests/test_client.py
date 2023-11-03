import unittest
from unittest.mock import patch

from dhl_sdk.client import Client
from dhl_sdk.authentication import APIKeyAuthentication


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
                offset=offset,
                name=name,
                unit_id=unit_id,
            )
            project = next(result)

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
