# Deprecated Code

This directory contains deprecated code that is kept for reference purposes only.

## entities.py & db_entities.py

**Status:** DEPRECATED - Do not use in new code

These modules contain legacy entity definitions that were manually written before the OpenAPI code generation was set up.

- `entities.py` - Legacy API entity models (Project, Model, Variable, etc.)
- `db_entities.py` - Legacy database entity models (Product, Experiment, Recipe, etc.)

### Migration Guide

Instead of using `dhl_sdk._deprecated.entities` or `dhl_sdk._deprecated.db_entities`, you should:

1. **Use OpenAPI-generated types** from the `api_types` package (generated in `dhl_api/`)
2. **Wrap them** with SDK-specific functionality as needed
3. **Only do basic Pydantic model matching** - validations are handled by the API

### Example

**Old approach (deprecated):**
```python
from dhl_sdk._deprecated.entities import Variable
from dhl_sdk._deprecated.db_entities import Product, Experiment
```

**New approach:**
```python
import api_types
# Wrap the generated types if needed
class Variable(api_types.Variable):
    # Add SDK-specific methods here
    pass

class Product(api_types.Product):
    # Add SDK-specific methods here
    pass
```

### Why was this deprecated?

- Manual type definitions diverged from the actual API schema
- OpenAPI code generation ensures types stay in sync with the API
- Reduces maintenance burden and potential for errors
- The API now handles all validations, so complex validation logic in the SDK is unnecessary

### How to use this for reference

You can look at the code in `entities.py` and `db_entities.py` to understand:
- What SDK-specific functionality was previously implemented
- How to wrap OpenAPI-generated types with similar functionality
- Patterns for working with the API entities
- What validation logic used to exist (now handled by API)

Do not import or use this code directly in new implementations.
