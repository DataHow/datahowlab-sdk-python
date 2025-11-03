import unittest
from unittest.mock import Mock

from openapi_client.models.process_format_code import ProcessFormatCode
from openapi_client.models.product import Product as OpenAPIProduct

from dhl_sdk.entities.product import Product, ProductRequest
from tests.entities._fixtures import create_product, VAR_1_ID, VAR_2_ID


class TestProduct(unittest.TestCase):
    api_product: OpenAPIProduct

    def setUp(self):
        self.api_product = create_product(
            id="prod-123",
            name="Test Product",
            code="TEST_PROD",
            description="A test product",
        )

    def test_init(self):
        product = Product(self.api_product)
        self.assertIsNotNone(product)

    def test_str(self):
        product = Product(self.api_product)
        result = str(product)
        self.assertEqual(result, "Product(name=Test Product, code=TEST_PROD)")

    def test_id_property(self):
        product = Product(self.api_product)
        self.assertEqual(product.id, "prod-123")

    def test_name_property(self):
        product = Product(self.api_product)
        self.assertEqual(product.name, "Test Product")

    def test_code_property(self):
        product = Product(self.api_product)
        self.assertEqual(product.code, "TEST_PROD")

    def test_description_property(self):
        product = Product(self.api_product)
        self.assertEqual(product.description, "A test product")

    def test_process_format_property(self):
        product = Product(self.api_product)
        self.assertIsNotNone(product.process_format)

    def test_variable_data_property_none(self):
        product = Product(self.api_product)
        result = product.variable_data
        self.assertEqual(result, {})

    def test_variable_data_property_with_data(self):
        self.api_product.variable_data = {VAR_1_ID: {"type": "scalar", "value": 5.5}}
        product = Product(self.api_product)
        result = product.variable_data

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn(VAR_1_ID, result)

    def test_variable_data_property_multiple_variables(self):
        self.api_product.variable_data = {VAR_1_ID: {"type": "scalar", "value": 5.5}, VAR_2_ID: {"type": "scalar", "value": 10.0}}
        product = Product(self.api_product)
        result = product.variable_data

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertIn(VAR_1_ID, result)
        self.assertIn(VAR_2_ID, result)

    def test_tags_property_none(self):
        product = Product(self.api_product)
        self.assertEqual(product.tags, {})

    def test_tags_property_dict(self):
        self.api_product.tags = {"key": "value"}
        product = Product(self.api_product)
        self.assertEqual(product.tags, {"key": "value"})


class TestProductRequest(unittest.TestCase):
    def test_new(self):
        request = ProductRequest.new(
            name="New Product",
            code="NEW_PROD",
            description="New product description",
            process_format=ProcessFormatCode.MAMMAL,
        )
        self.assertIsNotNone(request)

    def test_new_with_tags(self):
        request = ProductRequest.new(
            name="New Product",
            code="NEW_PROD",
            description="New product description",
            process_format=ProcessFormatCode.MAMMAL,
            tags={"tag1": "value1"},
        )
        self.assertIsNotNone(request)

    def test_new_with_variable_data_none(self):
        request = ProductRequest.new(
            name="New Product",
            code="NEW_PROD",
            description="New product description",
            process_format=ProcessFormatCode.MAMMAL,
            variable_data=None,
        )
        self.assertIsNotNone(request)

    def test_new_with_variable_data_single(self):
        variable_data = {VAR_1_ID: {"type": "scalar", "value": 5.5}}

        request = ProductRequest.new(
            name="New Product",
            code="NEW_PROD",
            description="New product description",
            process_format=ProcessFormatCode.MAMMAL,
            variable_data=variable_data,
        )
        self.assertIsNotNone(request)

    def test_new_with_variable_data_multiple(self):
        variable_data = {
            VAR_1_ID: {"type": "scalar", "value": 5.5},
            VAR_2_ID: {"type": "scalar", "value": 10.0},
        }

        request = ProductRequest.new(
            name="New Product",
            code="NEW_PROD",
            description="New product description",
            process_format=ProcessFormatCode.MAMMAL,
            variable_data=variable_data,
        )
        self.assertIsNotNone(request)

    def test_str(self):
        request = ProductRequest.new(
            name="New Product",
            code="NEW_PROD",
            description="New product description",
            process_format=ProcessFormatCode.MAMMAL,
        )
        result = str(request)
        self.assertEqual(result, "ProductRequest(name=New Product, code=NEW_PROD)")

    def test_create(self):
        mock_api = Mock()
        created_product = create_product(
            id="prod-456",
            name="Created Product",
            code="CREATED_PROD",
            description="Created product",
        )
        mock_api.create_product_api_v1_products_post.return_value = created_product

        request = ProductRequest.new(
            name="Created Product",
            code="CREATED_PROD",
            description="Created product",
            process_format=ProcessFormatCode.MAMMAL,
        )
        product = request.create(mock_api)

        self.assertIsInstance(product, Product)
        self.assertEqual(product.id, "prod-456")
        self.assertEqual(product.name, "Created Product")
        mock_api.create_product_api_v1_products_post.assert_called_once()

    def test_create_with_variable_data(self):
        variable_data = {VAR_1_ID: {"type": "scalar", "value": 5.5}}

        mock_api = Mock()
        created_product = create_product(
            id="prod-789",
            name="Product with Variables",
            code="PROD_VARS",
            description="Product with variable data",
        )
        created_product.variable_data = variable_data
        mock_api.create_product_api_v1_products_post.return_value = created_product

        request = ProductRequest.new(
            name="Product with Variables",
            code="PROD_VARS",
            description="Product with variable data",
            process_format=ProcessFormatCode.MAMMAL,
            variable_data=variable_data,
        )
        product = request.create(mock_api)

        self.assertIsInstance(product, Product)
        self.assertEqual(product.id, "prod-789")
        self.assertEqual(product.name, "Product with Variables")
        self.assertIsNotNone(product.variable_data)
        self.assertIn(VAR_1_ID, product.variable_data)
        mock_api.create_product_api_v1_products_post.assert_called_once()
