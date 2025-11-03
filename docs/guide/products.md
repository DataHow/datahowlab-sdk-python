# Products

Products represent the items or processes being tracked in DataHowLab.

## Creating Products

```python
product = client.create_product(
    code="PROD001",
    name="My Product",
    description="Product description"
)
```

## Listing Products

```python
# List all products
products = client.list_products()

# Filter by code
products = client.list_products(code="PROD")
```

## Getting a Product

```python
product = client.get_product(product_id="product-id")
```

## Updating Products

```python
updated = client.update_product(
    product_id=product.id,
    name="Updated Name",
    description="Updated description"
)
```

## Deleting Products

```python
client.delete_product(product_id=product.id)
```

For complete API details, see [Client API Reference](../api/client.md).
