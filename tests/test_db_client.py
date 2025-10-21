import unittest

# TODO: This entire test file tests deprecated functionality from dhl_sdk.db_entities and dhl_sdk.crud
# The following functionality needs to be restored using the OpenAPI client (dhl_api):
#
# 1. Product entity wrapper around openapi Product model with:
#    - Product.new() factory method for creating new products
#    - Product.requests() for CRUD operations
#    - Product.validate_import() for validation before import
#    - Product.create_request_body() for POST requests
#
# 2. Variable entity wrapper around openapi Variable model with:
#    - Variable.new() factory method supporting multiple variants:
#      * VariableNumeric (with optional default value)
#      * VariableCategorical (with default, strict mode, values list)
#      * VariableLogical (with default boolean value)
#      * VariableFlow (with type, stepSize, volumeId, references)
#    - Variable.requests() for CRUD operations
#    - Variable.validate_import() for validation before import
#    - Variable.create_request_body() for POST requests
#    - Variable group validation (X Variables, Z Variables, Feeds/Flows, etc.)
#
# 3. File entity for experiment file uploads with:
#    - File creation with name, description, type (runData), data (timeseries)
#    - File.create_file() for POST /api/db/v2/files
#    - File.validate_import() for checking data format
#    - PUT /api/db/v2/files/{id}/data for uploading timeseries data
#
# 4. Experiment entity wrapper around openapi Experiment model with:
#    - Experiment.new() factory method with product, variables, data
#    - Experiment.create_request_body() for POST requests
#    - Support for run experiments with startTime/endTime
#    - Support for variables list and instances
#
# 5. DataHowLabClient.create() method for importing entities:
#    - Takes Product, Variable, Experiment entities
#    - Calls validate_import() before creating
#    - Uses POST endpoints from OpenAPI client
#
# 6. Result[T] generic class for pagination:
#    - Iterator over paginated results
#    - Automatically fetches next pages as needed
#    - Integrates with entity requests classes
#
# 7. Import validation framework:
#    - ImportValidationException for validation errors
#    - NewEntityException for entity creation errors
#    - Validators for checking uniqueness (code, name) before import
#    - ExperimentFileValidator for checking file data format
#
# Reference files for migration:
# - dhl_sdk/_deprecated/db_entities.py - Entity definitions
# - dhl_sdk/_deprecated/entities.py - Legacy project/model types
# - tests/test_db_client.py (this file) - Test patterns to restore
