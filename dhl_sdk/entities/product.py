from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.product import Product as OpenAPIProduct
    from openapi_client.models.product_create import ProductCreate


class Product:
    def __init__(self, product: "OpenAPIProduct"):
        self._product = product

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
    def description(self) -> str | None:
        return self._product.description

    @property
    def process_format(self) -> Any:
        return self._product.process_format

    @property
    def variable_data(self) -> Any:
        return self._product.variable_data

    @property
    def tags(self) -> dict[str, Any] | None:
        return self._product.tags


class ProductRequest:
    def __init__(self, product_create: "ProductCreate"):
        self._product_create = product_create

    def __str__(self) -> str:
        return f"ProductRequest(name={self._product_create.name}, code={self._product_create.code})"

    @staticmethod
    def new(
        name: str,
        code: str,
        description: str,
        process_format: Any,
        tags: dict[str, Any] | None = None,
        variable_data: dict[str, Any] | None = None,
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
        from openapi_client.models.product import Product as OpenAPIProduct

        created_product: OpenAPIProduct = api.create_product_api_v1_products_post(product_create=self._product_create)
        return Product(created_product)
