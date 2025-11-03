"""
This module defines all the constants used across the project. Constants are
defined as variables with uppercase names to signify their immutability and
importance. This file serves as a single source of truth for static values
to improve code readability, maintainability, and consistency.
"""

# API Base Path
BASE_API_PATH = "/api/db/v2"

# API Endpoints (v2 SDK format with leading slash for proper URL joining)
PRODUCTS_URL = f"{BASE_API_PATH}/products"
RECIPES_URL = f"{BASE_API_PATH}/recipes"
FILES_URL = f"{BASE_API_PATH}/files"
EXPERIMENTS_URL = f"{BASE_API_PATH}/experiments"
VARIABLES_URL = f"{BASE_API_PATH}/variables"
GROUPS_URL = f"{BASE_API_PATH}/groups"
PROJECTS_URL = f"{BASE_API_PATH}/projects"
DATASETS_URL = f"{BASE_API_PATH}/datasets"
MODELS_URL = f"{BASE_API_PATH}/models"
PREDICT_URL = f"{BASE_API_PATH}/predict"

# Legacy endpoints (kept for backward compatibility)
TEMPLATES_URL = "api/db/v2/pipelineJobTemplates"
LEGACY_PREDICT_URL = "api/pipeline/v1/pipeline"

# Process Format UUIDs (v2 SDK values - updated 2025-01)
PROCESS_FORMAT_MAP = {
    "mammalian": "9c6b258f-6f07-4f18-aea3-e5e5bf703740",
    "microbial": "7fac2dea-6f23-4ce6-bc36-bdd3e47cf341",  # V2 SDK value (updated from legacy)
}

# Process Unit UUIDs
PROCESS_UNIT_MAP = {
    "cultivation": "04a324da-13a5-470b-94a1-bda6ac87bb86",
    "spectroscopy": "373c173a-1f23-4e56-874e-90ca4702ec0d",
}
