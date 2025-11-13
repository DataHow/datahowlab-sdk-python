#!/usr/bin/env python3
"""
Example: Creating a product in DataHowLab

This example demonstrates how to create a new product with the SDK.
"""

import random
import string
from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from dhl_sdk.entities.product import ProductRequest
from openapi_client.models.process_format_code import ProcessFormatCode


def main():
    # Initialize client
    key = APIKeyAuthentication()
    client = DataHowLabClient(auth_key=key, base_url="https://dev.datahowlab.ch/")

    # Generate unique code (must be <= 10 characters)
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    product_code = f"SDK-{suffix}"

    # Create product request
    product_request = ProductRequest.new(
        name=f"SDK Example Product {suffix}",
        code=product_code,
        description="Product created via SDK example",
        process_format=ProcessFormatCode.MAMMAL,
        tags={"example": "true", "source": "sdk"},
    )

    # Create the product
    product = product_request.create(client)

    # Display result
    print(f"Created product: {product.code}")
    print(f"  ID: {product.id}")
    print(f"  Name: {product.name}")


if __name__ == "__main__":
    main()
