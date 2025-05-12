# pylint: disable=missing-docstring
import unittest
from unittest.mock import Mock, call, patch

from pydantic import ValidationError

from dhl_sdk.authentication import APIKeyAuthentication
from dhl_sdk.client import DataHowLabClient
from dhl_sdk.crud import Result
from dhl_sdk.db_entities import (
    Experiment,
    File,
    FlowVariableReference,
    Product,
    Variable,
    VariableCategorical,
    VariableFlow,
    VariableLogical,
    VariableNumeric,
)
from dhl_sdk.exceptions import ImportValidationException, NewEntityException
from dhl_sdk.validators import ExperimentFileValidator


class TestProductEntity(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.get.return_value = Mock(
            json=lambda: [
                {
                    "id": "id-123",
                    "code": "code1",
                    "name": "product 1",
                    "description": "description 1",
                },
                {
                    "id": "id-456",
                    "code": "code2",
                    "name": "product 2",
                    "description": "description 2",
                },
            ],
            headers={"x-total-count": "2"},
        )

    def test_projects_list(self):
        projects, total = Product.requests(self.client).list(0, 10)

        self.assertEqual(total, 2)
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0].id, "id-123")
        self.assertEqual(projects[0].code, "code1")
        self.assertEqual(projects[1].name, "product 2")
        self.assertEqual(projects[1].description, "description 2")

    def test_projects_result(self):
        project_requests = Product.requests(self.client)
        result = Result[Product](5, {}, project_requests)

        p1 = next(result)

        self.assertEqual(p1.id, "id-123")
        self.assertEqual(p1.name, "product 1")

        p2 = next(result)

        self.assertEqual(p2.id, "id-456")
        self.assertEqual(p2.code, "code2")

    def test_new_product(self):
        with self.assertRaises(NewEntityException) as ex:
            product = Product.new("bigcodename", "name", "description")
            self.assertEqual(
                ex.exception.message,
                "Product code must be from 1 to 6 characters long",
            )

        product = Product.new("code", "name", "description")
        self.assertEqual(product.code, "code")
        self.assertEqual(product.name, "name")
        self.assertEqual(product.description, "description")

    def test_product_request_body(self):
        product = Product.new("code", "name", "description")
        self.assertEqual(
            product.create_request_body(),
            {"code": "code", "name": "name", "description": "description"},
        )

    def test_product_validation_success(self):
        client = Mock()

        client.get.return_value.headers = {"x-total-count": "0"}
        product = Product.new("code", "name", "description")

        self.assertTrue(product.validate_import(client))

    def test_product_validation_failure(self):
        client = Mock()

        client.get.return_value.headers = {"x-total-count": "1"}
        product = Product.new("code", "name", "description")

        with patch.object(product._validator, "is_imported", return_value=False):
            with self.assertRaises(ImportValidationException) as ex:
                product.validate_import(client)

        self.assertTrue(
            ex.exception.message.startswith("This product code code is already taken")
        )


class TestProductRequests(unittest.TestCase):
    def setUp(self):
        self.auth_key = APIKeyAuthentication("test_auth_key")
        self.base_url = "https://test.com"
        self.client = DataHowLabClient(self.auth_key, self.base_url)

    @patch("requests.Session.get")
    def test_products_imported(self, mock_get):
        product = Product.new("code", "name", "description")
        product.id = "id-123"

        _ = product._validator.is_imported(product, self.client._client)

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/products/id-123",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    def test_products_validation(self, mock_get):
        product = Product.new("code", "name", "description")

        mock_get.side_effect = [
            Mock(headers={"x-total-count": "0"}),
            Mock(headers={"x-total-count": "1"}),
        ]
        with patch.object(product._validator, "is_imported", return_value=False):
            with self.assertRaises(ImportValidationException):
                _ = product.validate_import(self.client._client)

        mock_get.assert_any_call(
            ("https://test.com/api/db/v2/products?filterBy[name]=name&archived=any"),
            headers={"Authorization": "ApiKey test_auth_key"},
        )

        mock_get.assert_any_call(
            ("https://test.com/api/db/v2/products?filterBy[code]=code&archived=any"),
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    @patch("requests.Session.post")
    def test_client_create_product(self, mock_post, mock_get):
        product = Product.new("code", "name", "description")
        client = DataHowLabClient(
            APIKeyAuthentication("test_auth_key"), "https://test.com"
        )

        mock_get.side_effect = [
            Mock(headers={"x-total-count": "0"}),
            Mock(headers={"x-total-count": "0"}),
        ]

        with patch.object(product._validator, "is_imported", return_value=False):
            with self.assertRaises(ValidationError):
                _ = client.create(product)

        mock_post.assert_called_once_with(
            "https://test.com/api/db/v2/products",
            headers={"Authorization": "ApiKey test_auth_key"},
            json={"code": "code", "name": "name", "description": "description"},
        )


class TestVariableEntity(unittest.TestCase):
    def setUp(self) -> None:
        self.variable_group_codes = {
            "X Variables": ("959606c1-44bc-4657-82ff-70c247be14aa", "X"),
            "Z Variables": ("77713a3b-0110-4c91-90db-a83d5e22a3e7", "Z"),
            "Feeds/Flows": ("4fb3f9e7-781b-4331-ac6d-ee7496fc5cec", "Feed"),
        }

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

    def test_new_variable(self):
        var = Variable.new(
            code="var1",
            name="Variable 1",
            description="description",
            variable_group="X Variables",
            variable_type=VariableNumeric(),
            measurement_unit="n",
        )

        var.group.validate_group(self.variable_group_codes)

        self.assertEqual(var.code, "var1")
        self.assertEqual(var.name, "Variable 1")
        self.assertEqual(var.description, "description")
        self.assertEqual(var.group.name, "X Variables")
        self.assertEqual(var.group.id, "959606c1-44bc-4657-82ff-70c247be14aa")
        self.assertEqual(var.group.code, "X")
        self.assertEqual(var.variant, "numeric")
        self.assertEqual(var.variant_details, VariableNumeric())

    @patch("requests.Session.get")
    def test_variable_request_numeric(self, mock_get):
        var = Variable.new(
            code="var1",
            name="Variable 1",
            description="description",
            variable_group="X Variables",
            variable_type=VariableNumeric(default=3.0),
            measurement_unit="n",
        )

        var.group.validate_group(self.variable_group_codes)

        self.assertEqual(
            var.create_request_body(),
            {
                "code": "var1",
                "name": "Variable 1",
                "description": "description",
                "variant": "numeric",
                "numeric": {"default": 3.0},
                "measurementUnit": "n",
                "group": {
                    "id": "959606c1-44bc-4657-82ff-70c247be14aa",
                },
            },
        )

    def test_variable_request_categorical(self):
        var = Variable.new(
            code="var1",
            name="Variable 1",
            description="description",
            variable_group="Z Variables",
            variable_type=VariableCategorical(
                default="a", strict=True, values=["a", "b", "c"]
            ),
            measurement_unit="n",
        )

        var.group.validate_group(self.variable_group_codes)

        self.assertEqual(
            var.create_request_body(),
            {
                "code": "var1",
                "name": "Variable 1",
                "description": "description",
                "variant": "categorical",
                "categorical": {
                    "default": "a",
                    "strict": True,
                    "values": ["a", "b", "c"],
                },
                "measurementUnit": "n",
                "group": {
                    "id": "77713a3b-0110-4c91-90db-a83d5e22a3e7",
                },
            },
        )

    def test_variable_request_logical(self):
        var = Variable.new(
            code="var1",
            name="Variable 1",
            description="description",
            variable_group="Z Variables",
            variable_type=VariableLogical(default=True),
            measurement_unit="n",
        )

        var.group.validate_group(self.variable_group_codes)

        self.assertEqual(
            var.create_request_body(),
            {
                "code": "var1",
                "name": "Variable 1",
                "description": "description",
                "variant": "logical",
                "logical": {
                    "default": True,
                },
                "measurementUnit": "n",
                "group": {
                    "id": "77713a3b-0110-4c91-90db-a83d5e22a3e7",
                },
            },
        )

    def test_variable_request_flows(self):
        var = Variable.new(
            code="FEED1",
            name="Feed 1",
            description="description",
            variable_group="Feeds/Flows",
            variable_type=VariableFlow(
                type="conti",
                stepSize=1000,
                volumeId="vol-id",
                references=[
                    FlowVariableReference(
                        measurementId="meas-id-111", concentrationId="conc-id-222"
                    )
                ],
            ),
            measurement_unit="n",
        )

        var.group.validate_group(self.variable_group_codes)

        self.assertEqual(
            var.create_request_body(),
            {
                "code": "FEED1",
                "name": "Feed 1",
                "description": "description",
                "variant": "flow",
                "flow": {
                    "type": "conti",
                    "stepSize": 1000,
                    "volumeId": "vol-id",
                    "references": [
                        {
                            "measurementId": "meas-id-111",
                            "concentrationId": "conc-id-222",
                        }
                    ],
                },
                "measurementUnit": "n",
                "group": {
                    "id": "4fb3f9e7-781b-4331-ac6d-ee7496fc5cec",
                },
            },
        )


class TestVariableRequests(unittest.TestCase):
    def setUp(self):
        self.auth_key = APIKeyAuthentication("test_auth_key")
        self.base_url = "https://test.com"
        self.client = DataHowLabClient(self.auth_key, self.base_url)

    @patch("requests.Session.get")
    def test_variable_imported(self, mock_get):
        var = Variable.new(
            code="var1",
            name="Variable 1",
            description="description",
            variable_group="X Variables",
            variable_type=VariableNumeric(default=3.0),
            measurement_unit="n",
        )
        var.id = "id-123"

        _ = var._validator.is_imported(var, self.client._client)

        mock_get.assert_called_once_with(
            "https://test.com/api/db/v2/variables/id-123",
            headers={"Authorization": "ApiKey test_auth_key"},
        )

    @patch("requests.Session.get")
    def test_variables_validation(self, mock_get):
        var = Variable.new(
            code="var1",
            name="Variable 1",
            description="description",
            variable_group="X Variables",
            variable_type=VariableNumeric(default=3.0),
            measurement_unit="n",
        )

        mock_group_json = Mock()
        mock_group_json.json.return_value = [
            {
                "name": "X Variables",
                "id": "959606c1-44bc-4657-82ff-70c247be14aa",
                "code": "X",
            }
        ]

        mock_get.side_effect = [
            mock_group_json,
            Mock(headers={"x-total-count": "0"}),
            Mock(headers={"x-total-count": "1"}),
        ]

        with patch.object(var._validator, "is_imported", return_value=False):
            with self.assertRaises(ImportValidationException):
                _ = var.validate_import(self.client._client)

            mock_get.assert_has_calls(
                [
                    call(
                        "https://test.com/api/db/v2/groups",
                        headers={"Authorization": "ApiKey test_auth_key"},
                    ),
                    call(
                        (
                            "https://test.com/api/db/v2/variables?"
                            "filterBy[code]=var1&filterBy[group._id]="
                            "959606c1-44bc-4657-82ff-70c247be14aa&archived=any"
                        ),
                        headers={"Authorization": "ApiKey test_auth_key"},
                    ),
                    call(
                        (
                            "https://test.com/api/db/v2/variables?"
                            "filterBy[name]=Variable+1&filterBy[group._id]="
                            "959606c1-44bc-4657-82ff-70c247be14aa&archived=any"
                        ),
                        headers={"Authorization": "ApiKey test_auth_key"},
                    ),
                ]
            )


class TestFileEntity(unittest.TestCase):
    def setUp(self) -> None:
        data = {
            "var1": {"timestamps": [1, 2, 3], "values": [10, 20, 30]},
            "var2": {"timestamps": [7, 8, 9], "values": [70, 80, 90]},
        }

        self.file = File(
            name="file1",
            description="description1",
            type="run",
            data=data,
            validator=ExperimentFileValidator(),
        )

    def test_file_request_body(self):
        self.assertEqual(
            self.file.create_request_body(),
            {
                "name": "file1",
                "description": "description1",
                "type": "runData",
            },
        )

    def test_file_validation_success(self):
        mock_var1 = Mock()
        mock_var1.code = "var1"
        mock_var2 = Mock()
        mock_var2.code = "var2"

        variables = [mock_var1, mock_var2]

        self.assertTrue(
            self.file.validate_import(
                variables,
                {
                    "startTime": "1970-01-01T00:00:00Z",
                    "endTime": "1970-01-02T01:00:00Z",
                },
            )
        )

    def test_file_validation_failure(self):
        mock_var1 = Mock()
        mock_var1.code = "var1"
        mock_var2 = Mock()
        mock_var2.code = "var2"

        variables = [mock_var1, mock_var2]

        data = {
            "var1": {"values": [10, 20, 30]},
            "var2": {"timestamps": [7, 8, 9], "values": [70, 80, 90]},
        }

        file = File(
            name="file1",
            description="description1",
            type="run",
            data=data,
            validator=ExperimentFileValidator(),
        )

        with self.assertRaises(ImportValidationException) as ex:
            file.validate_import(variables)

        data = {
            "var1": [1, 2, 3],
            "var2": {"values": [70, 80, 90]},
        }
        file._data = data

        with self.assertRaises(ImportValidationException) as ex:
            file.validate_import(variables)

        data = {
            "var1": {"timestamps": [1, 2, 3], "values": [10, 20, 30]},
        }

        file._data = data
        with self.assertRaises(ImportValidationException) as ex:
            file.validate_import(variables)


class TestFileRequests(unittest.TestCase):
    def setUp(self):
        self.auth_key = APIKeyAuthentication("test_auth_key")
        self.base_url = "https://test.com"
        self.client = DataHowLabClient(self.auth_key, self.base_url)

    @patch("requests.Session.post")
    @patch("requests.Session.put")
    def test_files_create_success(self, mock_put, mock_post):
        file = File(
            name="file1",
            description="description1",
            type="run",
            data={
                "var1": {"timestamps": [1, 2, 3], "values": [10, 20, 30]},
                "var2": {"timestamps": [7, 8, 9], "values": [70, 80, 90]},
            },
            validator=ExperimentFileValidator(),
        )

        mock_post.return_value.json.return_value = {"id": "file-id-123"}

        file_id = file.create_file(self.client._client)

        mock_post.assert_called_once_with(
            "https://test.com/api/db/v2/files",
            headers={"Authorization": "ApiKey test_auth_key"},
            json={
                "name": "file1",
                "description": "description1",
                "type": "runData",
            },
        )

        mock_put.assert_called_once_with(
            "https://test.com/api/db/v2/files/file-id-123/data",
            headers={"Authorization": "ApiKey test_auth_key"},
            json={
                "timeseries": {
                    "var1": {"timestamps": [1, 2, 3], "values": [10, 20, 30]},
                    "var2": {"timestamps": [7, 8, 9], "values": [70, 80, 90]},
                }
            },
        )

        self.assertEqual(file_id, "file-id-123")


class TestExperimentsEntity(unittest.TestCase):
    def setUp(self):
        self.var1 = Variable.new(
            code="var1",
            name="var1",
            description="desc1",
            variable_group="X Variables",
            variable_type=VariableNumeric(),
            measurement_unit="n",
        )
        self.var1.id = "var1-id"

        self.var2 = Variable.new(
            code="var2",
            name="var2",
            description="desc2",
            variable_group="Z Variables",
            variable_type=VariableCategorical(),
            measurement_unit="n",
        )
        self.var2.id = "var2-id"

        self.product = Product.new("prod", "product 1", "product description")
        self.product.id = "prod-id"

        data = {
            "var1": {"timestamps": [1, 2, 3], "values": [10, 20, 30]},
            "var2": {"timestamps": [7, 8, 9], "values": [70, 80, 90]},
        }

        self.experiment = Experiment.new(
            name="exp name",
            product=self.product,
            description="exp description",
            variables=[self.var1, self.var2],
            data_type="run",
            data=data,
            variant="run",
            start_time="2020-09-21T08:45:50Z",
            end_time="2020-10-05T08:45:50Z",
        )

    def test_experiment_request_body(self):
        self.assertEqual(
            self.experiment.create_request_body(),
            {
                "name": "exp name",
                "description": "exp description",
                "product": {"id": "prod-id"},
                "variables": [{"id": "var1-id"}, {"id": "var2-id"}],
                "subunit": "",
                "variant": "run",
                "instances": [],
                "run": {
                    "startTime": "2020-09-21T08:45:50Z",
                    "endTime": "2020-10-05T08:45:50Z",
                },
            },
        )
