#!/usr/bin/env python3
"""
Example: Creating and uploading an experiment to DataHowLab

This example demonstrates how to:
1. Create a product
2. Create variables with different types (numeric, categorical)
3. Create an experiment with time-series data

Note: This script requires DHL_API_KEY environment variable to be set.
Note: Resources are created with random suffixes to avoid collisions.
"""

import random
import string
from datetime import datetime
from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from dhl_sdk.entities.product import ProductRequest
from dhl_sdk.entities.variable import VariableRequest
from dhl_sdk.entities.experiment import ExperimentRequest
from openapi_client.models.process_format_code import ProcessFormatCode
from openapi_client.models.process_unit_code import ProcessUnitCode
from openapi_client.models.numeric_details_input import NumericDetailsInput
from openapi_client.models.categorical_details_input import CategoricalDetailsInput
from openapi_client.models.variantdetails1 import Variantdetails1


def random_suffix(length=6):
    """Generate a random alphanumeric suffix for unique naming."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def main():
    """Main function to demonstrate experiment upload workflow."""

    # Initialize client
    print("Initializing DataHowLab client...")
    key = APIKeyAuthentication()
    base_url = "https://dev.datahowlab.ch/"

    client = DataHowLabClient(auth_key=key, base_url=base_url)
    print(f"   ✓ Connected to {base_url}")

    # Generate random suffix for unique naming
    suffix = random_suffix()
    print(f"   ✓ Using random suffix: {suffix}")

    try:
        # Step 1: Create a product
        print("\n1. Creating product...")
        product_code = f"SDK-{suffix}"  # Keep under 10 chars

        product_request = ProductRequest.new(
            name=f"SDK Example Product {suffix}",
            code=product_code,
            description="Product created via SDK example",
            process_format=ProcessFormatCode.MAMMAL,
            tags={"example": "true", "source": "sdk", "random_suffix": suffix},
        )
        product = product_request.create(client)
        print(f"   ✓ Created product: {product.name} (ID: {product.id}, Code: {product.code})")

        # Step 2: Get existing variables (instead of creating new ones due to OpenAPI generator issue)
        print("\n2. Getting existing variables...")
        print("   Note: Using existing variables due to OpenAPI deserialization issue with variable creation.")

        # Get Temperature variable
        temp_vars = list(client.get_variables(search="Temperature"))
        if not temp_vars:
            raise ValueError("No Temperature variable found. Please create one manually first.")
        var1 = temp_vars[0]
        print(f"   ✓ Using variable: {var1.name} (ID: {var1.id}, Code: {var1.code})")

        # Get a categorical variable
        cat_vars = list(client.get_variables(search="Phase"))
        if not cat_vars:
            # Try another common categorical
            cat_vars = list(client.get_variables(search=""))
            cat_vars = [v for v in cat_vars if "categorical" in str(v.variant_details).lower()][:1]
        if not cat_vars:
            raise ValueError("No categorical variable found. Using Temperature for all.")
        var2 = cat_vars[0] if cat_vars else var1
        print(f"   ✓ Using variable: {var2.name} (ID: {var2.id}, Code: {var2.code})")

        # Get pH variable
        ph_vars = list(client.get_variables(search="pH"))
        if not ph_vars:
            ph_vars = temp_vars  # Fallback to temperature
        var3 = ph_vars[0]
        print(f"   ✓ Using variable: {var3.name} (ID: {var3.id}, Code: {var3.code})")

        # Step 5: Prepare experiment data
        print("\n3. Preparing experiment data...")
        # Data in compatibility format (variable code -> timestamps/values)
        compat_data = {
            var1.code: {
                "timestamps": [1600674350, 1600760750, 1600847150],  # Unix timestamps
                "values": [36.5, 37.0, 36.8],
            },
            var2.code: {"timestamps": [1600674350], "values": ["Growth"]},
            var3.code: {"timestamps": [1600674350, 1600760750, 1600847150], "values": [7.0, 7.1, 7.05]},
        }

        # Convert to OpenAPI format
        variables = [var1, var2, var3]
        openapi_data = ExperimentRequest.from_compat_data(variables, compat_data)  # pyright: ignore[reportArgumentType] - compat_data is dynamically typed dict, validated at runtime by from_compat_data
        print("   ✓ Data prepared and converted to OpenAPI format")

        # Step 6: Create experiment
        print("\n4. Creating experiment...")
        experiment_request = ExperimentRequest.new(
            name=f"SDK-Example-{suffix}",
            description="Experiment created via SDK example script",
            product=product,
            process_unit=ProcessUnitCode.BR,
            start_time=datetime.fromisoformat("2020-09-21T08:45:50+00:00"),
            end_time=datetime.fromisoformat("2020-10-05T08:45:50+00:00"),
            data=openapi_data,  # pyright: ignore[reportArgumentType] - from_compat_data returns dict with Optional values for null handling, but API filters them out
            tags={"example": "true", "source": "sdk", "random_suffix": suffix},
        )
        experiment = experiment_request.create(client)
        print(f"   ✓ Created experiment: {experiment.display_name} (ID: {experiment.id})")

        # Step 7: Verify the created experiment
        print("\n5. Verifying experiment...")
        retrieved_data = experiment.get_data_compat()
        print(f"   ✓ Retrieved data for {len(retrieved_data)} variables")
        for var_code, data in retrieved_data.items():
            if data:
                print(f"     - {var_code}: {len(data['values'])} data points")

        print("\n✓ SUCCESS! Experiment created and verified.")
        print(f"\nAll resources created with suffix: {suffix}")
        print(f"  - Product: {product.code}")
        print(f"  - Variables: {var1.code}, {var2.code}, {var3.code}")
        print(f"  - Experiment: {experiment.display_name}")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
