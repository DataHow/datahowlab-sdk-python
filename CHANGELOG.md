# Changelog

All notable changes to the DataHowLab SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-28

### 🚨 Breaking Changes

This is a complete rewrite of the SDK with breaking changes to nearly all APIs.

#### Client Architecture
- **Removed**: Dual client structure (`Client` and `DataHowLabClient`)
- **Changed**: Single unified `DataHowLabClient` class
- **Changed**: Initialization now requires explicit `api_key` parameter (or `DHL_API_KEY` env var)
- **Removed**: `APIKeyAuthentication` class (authentication now handled internally)

#### Entity Creation
- **Changed**: Direct creation methods on client (e.g., `client.create_product()`)
- **Removed**: Separate `.new()` + `.create()` pattern
- **Removed**: Need to reassign after creation to get ID
- **Changed**: All entity creation returns object with ID immediately

#### Variable System
- **Changed**: Variable types now use discriminated unions (`NumericVariable`, `CategoricalVariable`, etc.)
- **Removed**: Separate `VariableNumeric`, `VariableCategorical` classes at top level
- **Changed**: Variable type specified via `type` parameter with type instance
- **Improved**: Better validation at construction time

#### Data Structures
- **Added**: `ExperimentData` and `SpectraExperimentData` Pydantic models
- **Added**: `TimeseriesData` model with built-in validation
- **Changed**: Data must be provided as typed structures, not plain dicts
- **Improved**: Timestamp validation happens at creation time
- **Changed**: Datetime objects used instead of ISO strings

#### Predictions
- **Changed**: Unified `model.predict()` interface across all model types
- **Added**: Typed input classes (`SpectraPredictionInput`, `PropagationPredictionInput`, `HistoricalPredictionInput`)
- **Removed**: Separate preprocessor classes (now internal)
- **Changed**: Structured `PredictionOutput` with consistent format

#### Error Handling
- **Added**: Structured exception hierarchy
- **Added**: `ValidationError`, `EntityNotFoundError`, `EntityAlreadyExistsError`, `PredictionError`, `APIError`, `AuthenticationError`
- **Changed**: All errors include `code` and `details` attributes
- **Improved**: Better error messages with field-level information

#### File Handling
- **Removed**: `File` class from public API
- **Removed**: `UnresolvedInstance` from public API
- **Changed**: File uploads handled automatically during entity creation
- **Improved**: No manual file management required

#### Other Removals
- **Removed**: `CRUDClient` abstraction
- **Removed**: Separate validator classes
- **Removed**: `Result[T]` iterator (replaced with simple lists for most operations)
- **Removed**: `.requests()` static method pattern
- **Removed**: Protocol classes from public API

### ✨ New Features

- **Type Safety**: Full type hint support with mypy compatibility
- **Pydantic Validation**: All data structures validated at construction time
- **Structured Errors**: Programmatic error handling with detailed context
- **Simplified API**: 50% reduction in code required for common tasks
- **Better Defaults**: Sensible defaults for optional parameters
- **Method Chaining**: Where appropriate
- **IDE Support**: Complete autocomplete and type checking
- **py.typed Marker**: PEP 561 compliance for type checkers

### 📚 Documentation

- Complete rewrite of README.md with v2 examples
- New MIGRATION_GUIDE.md with before/after comparisons
- Updated examples.ipynb with v2 patterns
- Comprehensive docstrings on all public methods
- Updated validations.md for new data structures

### 🔧 Internal Changes

- Removed 9 files, added 4 files (~50% code reduction)
- Eliminated abstraction layers (validators, protocols, CRUDClient)
- Unified HTTP client implementation
- Internal file handling for experiments
- Cleaner separation of concerns

### 📦 Dependencies

No changes to runtime dependencies:
- pydantic ^2.4.2
- requests ^2.31.0
- numpy ^1.26.1

### ⚠️ Migration Notes

**This release requires code changes.** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions.

Key migration steps:
1. Update client initialization
2. Change entity creation patterns
3. Update variable type usage
4. Wrap experiment data in typed structures
5. Update prediction API calls
6. Update error handling

### 🙏 Acknowledgments

Thank you to all users who provided feedback on v1. This rewrite addresses the most common pain points while maintaining compatibility with the same underlying API.

---

## [0.3.1] - 2024-XX-XX (Previous Release)

Previous version with dual client architecture and separate validation layers.

See git history for older changelog entries.
