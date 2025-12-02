# Agent Guidelines for datahowlab-sdk-python

## Build/Test Commands

- Install dependencies: `uv sync` or `poetry install`
- Run all tests: `pytest` or `poetry run pytest`
- Run single test: `pytest tests/test_client.py::TestClient::test_init`
- Run with coverage: `pytest --cov=./ --cov-report=xml`
- Lint: `ruff check .` (auto-fix: `ruff check . --fix`)
- Format: `ruff format .`
- Type check: `basedpyright` (recommended mode configured)
- Regenerate OpenAPI types:
  `openapi-generator-cli generate -i openapi.json -g python -o dhl_api --global-property=apiTests=false,modelTests=false`

## Code Style & Architecture

- Line length: 140 characters (configured in pyproject.toml)
- Python version: >=3.10, <=3.13 (minimum 3.10)
- Use ruff for linting and formatting (replaces black/pylint)
- Type hints: Use standard library `typing` module (e.g., `Optional`, `Union`,
  `Literal`, `Type`, `TypeVar`)
- Imports: Group stdlib, third-party (requests, pydantic, numpy), then local
  (dhl_sdk.*); avoid wildcards
- Models: Use Pydantic v2 with `BaseModel`, `ConfigDict`, `Field`,
  `PrivateAttr`, `model_validator`
- Docstrings: Use NumPy style with Parameters/Returns sections
- Testing: Use `unittest` framework with `unittest.mock` for mocking
- Naming: snake_case for functions/variables, PascalCase for classes, use
  descriptive names

### Type Checking and Type Ignores

- **Goal**: Achieve 0 errors and 0 warnings in `basedpyright`
- **Type ignore comments are last resort**: Try first to check dynamic type,
  ownership of member, or model_validate() for Pydantic types, if available, to
  achieve type safety
- **Type ignore comments MUST include explanations** - explain WHY the ignore is
  necessary and why it can't be fixed differently
- **Format**:
  `# pyright: ignore[errorCode] - Clear explanation of why this is unavoidable`

## Important Project Context

- **NEVER modify `dhl_api/` package** - it is auto-generated from openapi.json
- **`dhl_sdk/_deprecated/entities.py` is DEPRECATED** - use only for reference;
  wrap openapi-generated types instead
- **`dhl_sdk/_deprecated/db_entities.py` is DEPRECATED** - use only for
  reference; wrap openapi-generated types instead
- Currently migrating from custom db types to openapi-generated types (work in
  progress)
- Validations are implemented in the API - only do basic pydantic model matching
  in SDK
- `dhl_sdk/exceptions.py` is mostly obsolete - being replaced by diagnostics
  from API
- See `dhl_sdk/_deprecated/README.md` for migration guide from deprecated code

## Examples and Compatibility

- **Keep examples working during refactoring** - maintain backwards
  compatibility where possible
- Example locations:
  - `examples.ipynb` - Jupyter notebook with comprehensive SDK usage examples
  - `README.md` sections: "Importing Package", "Data Accessing", "Data
    Importing", "Model Predictions"
- Test examples after making SDK changes to ensure they still work
