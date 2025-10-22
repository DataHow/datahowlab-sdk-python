# TODO: This entire test file tests deprecated functionality from dhl_sdk._input_processing and dhl_sdk._utils
# The following functionality needs to be evaluated for migration or deprecation:
#
# 1. Spectra preprocessing for model predictions:
#    - SpectraPreprocessor class for validating and formatting spectra data
#    - validate_spectra_format() for checking spectra array format
#    - Support for models with/without additional inputs
#    - Spectra dimension validation against model.spectra_size
#    - format() method to convert spectra to API request format
#
# 2. Cultivation preprocessing for propagation models:
#    - CultivationPropagationPreprocessor class
#    - Timestamp validation and unit conversion (s, m, h, d)
#    - Input validation for X Variables (initial values), W Variables (complete timeseries)
#    - format() method to convert inputs to API request format
#
# 3. Cultivation preprocessing for historical models:
#    - CultivationHistoricalPreprocessor class
#    - Steps validation (must start at 0, ascending order)
#    - Input validation for all model variables
#    - Timestamp and steps must have same length
#
# 4. Prediction response formatting:
#    - format_predictions() to convert API responses to user-friendly dict format
#    - Instance class for prediction values with confidence bounds
#    - PredictionResponse class for API response structure
#    - PredictionRequestConfig class for configuring predictions
#
# 5. Result[T] iterator for pagination (overlaps with test_db_client.py TODO)
#
# Decision needed: Are model predictions still supported in the OpenAPI?
# If yes, these utilities need to be migrated to work with OpenAPI model endpoints.
# If no, this file can be fully deprecated.
#
# Reference files for migration:
# - dhl_sdk/_input_processing.py (if exists) - Preprocessing logic
# - dhl_sdk/_utils.py (if exists) - Utility classes
# - tests/test_utils.py (this file) - Test patterns for preprocessing
