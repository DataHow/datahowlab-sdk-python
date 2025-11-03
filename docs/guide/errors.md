# Error Handling

The SDK provides structured exception classes for different error scenarios.

## Exception Hierarchy

All SDK exceptions inherit from `DHLError`:

```python
from dhl_sdk import DHLError

try:
    client.get_product("invalid-id")
except DHLError as e:
    print(f"SDK error: {e.message}")
    print(f"Error code: {e.code}")
```

## Specific Exceptions

### EntityNotFoundError

Raised when an entity doesn't exist:

```python
from dhl_sdk import EntityNotFoundError

try:
    product = client.get_product("nonexistent-id")
except EntityNotFoundError as e:
    print(f"Entity type: {e.entity_type}")
    print(f"Entity ID: {e.entity_id}")
```

### ValidationError

Raised for invalid input data:

```python
from dhl_sdk import ValidationError

try:
    product = client.create_product(code="INVALID CODE")  # Spaces not allowed
except ValidationError as e:
    print(f"Validation errors: {e.validation_errors}")
```

### AuthenticationError

Raised for authentication issues (401):

```python
from dhl_sdk import AuthenticationError

try:
    client = DataHowLabClient(api_key="invalid")
    client.list_products()
except AuthenticationError as e:
    print("Invalid API key")
```

### ServerError

Raised for server-side errors (500+):

```python
from dhl_sdk import ServerError

try:
    products = client.list_products()
except ServerError as e:
    print(f"Server error: {e.status_code}")
```

For complete exception reference, see [Errors API Reference](../api/errors.md).
