"""
This module defines all the constants used across the project. Constants are
defined as variables with uppercase names to signify their immutability and
importance. This file serves as a single source of truth for static values
to improve code readability, maintainability, and consistency.
"""

DB_PRODUCTS_URL = "api/db/v2/products"
DB_RECIPES_URL = "api/db/v2/recipes"
DB_FILES_URL = "api/db/v2/files"
DB_EXPERIMENTS_URL = "api/db/v2/experiments"
DB_VARIABLES_URL = "api/db/v2/variables"
DB_GROUPS_URL = "api/db/v2/groups"

EXT_PROJECTS_URL = "api/ext/v1/projects"
EXT_MODELS_URL = "api/ext/v1/models"


PROCESS_UNIT_MAP = {
    "cultivation": "04a324da-13a5-470b-94a1-bda6ac87bb86",
    "spectroscopy": "373c173a-1f23-4e56-874e-90ca4702ec0d",
}
