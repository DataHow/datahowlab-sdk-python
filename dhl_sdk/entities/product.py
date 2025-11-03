from typing import TYPE_CHECKING
from typing_extensions import override

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.process_format_code import ProcessFormatCode
    from openapi_client.models.product import Product as OpenAPIProduct
    from openapi_client.models.product_create import ProductCreate
    from openapi_client.models.raw_experiment_data_input_value import RawExperimentDataInputValue


class Product:
    _product: "OpenAPIProduct"

    def __init__(self, product: "OpenAPIProduct"):
        self._product = product

    @override
    def __str__(self) -> str:
        return f"Product(name={self._product.name}, code={self._product.code})"

    @property
    def id(self) -> str:
        return self._product.id

    @property
    def name(self) -> str:
        return self._product.name

    @property
    def code(self) -> str:
        return self._product.code

    @property
    def description(self) -> str:
        return self._product.description

    @property
    def process_format(self) -> "ProcessFormatCode":
        return self._product.process_format

    @property
    def variable_data(self) -> dict[str, "RawExperimentDataInputValue"]:
        return self._product.variable_data or {}

    @property
    def tags(self) -> dict[str, str]:
        return self._product.tags or {}


class ProductRequest:
    _product_create: "ProductCreate"

    def __init__(self, product_create: "ProductCreate"):
        self._product_create = product_create

    @override
    def __str__(self) -> str:
        return f"ProductRequest(name={self._product_create.name}, code={self._product_create.code})"

    @staticmethod
    def new(
        name: str,
        code: str,
        description: str,
        process_format: "ProcessFormatCode",
        tags: dict[str, str] | None = None,
        variable_data: dict[str, "RawExperimentDataInputValue"] | None = None,
    ) -> "ProductRequest":
        from openapi_client.models.product_create import ProductCreate

        product_create = ProductCreate(
            name=name,
            code=code,
            description=description,
            processFormat=process_format,
            tags=tags,
            variableData=variable_data,
        )
        return ProductRequest(product_create)

    def create(self, api: "DefaultApi") -> Product:
        created_product = api.create_product_api_v1_products_post(product_create=self._product_create)
        return Product(created_product)
