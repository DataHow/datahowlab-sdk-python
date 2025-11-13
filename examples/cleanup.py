"""
Cleanup script for SDK example entities

Deletes products, variables, and experiments created by SDK examples.
Identifies them by the "sdk-example: true" tag.

Usage:
    python examples/cleanup.py [--dry-run] [--base-url URL]

Environment Variables:
    DHL_API_KEY - Your DataHowLab API key (required)
"""

import argparse
import sys
import requests
from dhl_sdk import DataHowLabClient, APIKeyAuthentication
from example_config import DHL_BASE_URL  # pyright: ignore[reportMissingImports] - examples are standalone scripts, not a package


def delete_entity(base_url: str, api_key: str, entity_type: str, entity_id: str) -> tuple[bool, str]:
    """
    Delete an entity using the REST API.

    Parameters
    ----------
    base_url : str
        Base URL for the API
    api_key : str
        API key for authentication
    entity_type : str
        Type of entity (products, experiments, variables)
    entity_id : str
        ID of the entity to delete

    Returns
    -------
    tuple[bool, str]
        Success flag and error message (if any)
    """
    url = f"{base_url.rstrip('/')}/api/v1/{entity_type}/{entity_id}"
    headers = {"Api-Key": api_key}

    try:
        response = requests.delete(url, headers=headers, timeout=30)
        response.raise_for_status()
        return True, ""
    except requests.exceptions.RequestException as e:
        return False, str(e)


# Parse command line arguments
parser = argparse.ArgumentParser(description="Cleanup SDK example entities")
parser.add_argument(
    "--base-url",
    default=DHL_BASE_URL,
    help="Base URL for the DataHowLab API",
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="List entities that would be deleted without actually deleting them",
)
args = parser.parse_args()

# Initialize client
try:
    auth = APIKeyAuthentication()
    api_key = auth.api_key
except ValueError as e:
    print(f"Error: {e}")
    print("\nPlease set the DHL_API_KEY environment variable:")
    print("  export DHL_API_KEY=your_api_key_here")
    sys.exit(1)

client = DataHowLabClient(auth_key=auth, base_url=args.base_url)

# Track deletion statistics
stats = {
    "experiments": {"found": 0, "deleted": 0, "failed": 0},
    "products": {"found": 0, "deleted": 0, "failed": 0},
    "variables": {"found": 0, "deleted": 0, "failed": 0},
}

# Delete experiments first (must be deleted before products/variables)
experiments = list(client.get_experiments(tags={"sdk-example": "true"}))
stats["experiments"]["found"] = len(experiments)

for exp in experiments:
    if args.dry_run:
        print(f"Would delete experiment: {exp.display_name}")
    else:
        success, error = delete_entity(args.base_url, api_key, "experiments", exp.id)
        if success:
            stats["experiments"]["deleted"] += 1
        else:
            print(f"Failed to delete experiment {exp.display_name}: {error}")
            stats["experiments"]["failed"] += 1

# Delete products created by examples
products = list(client.get_products(tags={"sdk-example": "true"}))
stats["products"]["found"] = len(products)

for product in products:
    if args.dry_run:
        print(f"Would delete product: {product.code} - {product.name}")
    else:
        success, error = delete_entity(args.base_url, api_key, "products", product.id)
        if success:
            stats["products"]["deleted"] += 1
        else:
            print(f"Failed to delete product {product.code}: {error}")
            stats["products"]["failed"] += 1

# Delete variables created by examples
variables = list(client.get_variables(tags={"sdk-example": "true"}))
stats["variables"]["found"] = len(variables)

for var in variables:
    if args.dry_run:
        print(f"Would delete variable: {var.code} - {var.name}")
    else:
        success, error = delete_entity(args.base_url, api_key, "variables", var.id)
        if success:
            stats["variables"]["deleted"] += 1
        else:
            print(f"Failed to delete variable {var.code}: {error}")
            stats["variables"]["failed"] += 1

# Print summary
print("\nCleanup Summary:")
for entity_type, counts in stats.items():
    print(f"  {entity_type.capitalize()}: {counts['found']} found", end="")
    if not args.dry_run:
        print(f", {counts['deleted']} deleted, {counts['failed']} failed")
    else:
        print()

if args.dry_run:
    print("\n(Dry run - no entities were deleted)")
    print("Run without --dry-run to delete these entities")
