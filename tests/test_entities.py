import unittest

# TODO: This entire test file tests deprecated functionality from dhl_sdk._deprecated.entities
# The following functionality needs to be evaluated for migration or deprecation:
#
# 1. Project entity types - DEPRECATED:
#    - CultivationProject class and process unit differentiation
#    - SpectraProject class
#    - Project.get_models() method
#    These are replaced by unified Project type from OpenAPI
#
# 2. Model entity types - DEPRECATED:
#    - SpectraModel class for spectroscopy models
#    - CultivationPropagationModel class
#    - CultivationHistoricalModel class
#    - ModelFactory for selecting model type based on process unit
#    These need to be replaced with model endpoints from OpenAPI:
#    - GET /api/db/v2/pipelineJobs (or similar model endpoints)
#    - Wrapper classes around openapi model types
#
# 3. Variable.requests() for legacy entity fetching:
#    - GET /api/db/v2/variables/{id}
#    This is now available through DataHowLabClient.get_variables()
#
# 4. Result[T] iterator pattern:
#    - Pagination over projects, models, variables
#    This functionality needs to be restored (see test_db_client.py TODO)
#
# Reference files for migration:
# - dhl_sdk/_deprecated/entities.py - Legacy entity definitions
# - tests/test_entities.py (this file) - Test patterns that may need updating
#
# Decision needed: Should model-related functionality be restored or fully deprecated?
