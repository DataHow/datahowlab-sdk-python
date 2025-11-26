"""
Example: Creating a product

Demonstrates how to create a new product with basic metadata and tags.
"""

import random
import string
from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from dhl_sdk.entities.product import ProductRequest
from openapi_client.models.process_format_code import ProcessFormatCode
from example_config import DHL_BASE_URL  # pyright: ignore[reportMissingImports] - examples are standalone scripts, not a package

# Initialize the client
key = APIKeyAuthentication()
client = DataHowLabClient(auth_key=key, base_url=DHL_BASE_URL)

# Generate unique code (maximum 10 characters)
suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
product_code = f"SDK-{suffix}"

# Create a product request with required fields
product_request = ProductRequest.new(
    name=f"SDK Example Product {suffix}",
    code=product_code,
    description="Product created via SDK example",
    process_format=ProcessFormatCode.MAMMAL,
    tags={"sdk-example": "true"},  # Tag for easy cleanup later
)

# Submit the request to create the product
product = product_request.create(client)

# The created product now has an ID and can be used in experiments
# product.id, product.code, product.name are available
