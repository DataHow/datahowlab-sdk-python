from typing import Any

from openapi_client.models.model import Model as OpenAPIModel
from openapi_client.models.model_status import ModelStatus
from openapi_client.models.model_type import ModelType
from openapi_client.models.product import Product as OpenAPIProduct
from openapi_client.models.process_format_code import ProcessFormatCode
from openapi_client.models.process_unit_code import ProcessUnitCode
from openapi_client.models.project import Project as OpenAPIProject
from openapi_client.models.variable import Variable as OpenAPIVariable
from openapi_client.models.variantdetails import Variantdetails

MODEL_ID = "a67f42c6-c77d-437a-a5bf-3090aa0d6ad9"
PROJECT_ID = "3b3ea4d3-a066-474b-aef6-41647654fe32"
DATASET_ID = "bb6d1875-6c2a-4d97-bba5-1af9f2378b97"
PRODUCT_ID = "440cf6a1-f8df-4024-a2eb-76d1027ae18f"
VARIABLE_ID = "0b31ec0b-2520-4300-a367-75ff25830b7b"

VAR_1_ID = "db0ed94c-5cc9-48dd-b5bc-58f15b4b6797"
VAR_2_ID = "f54a8afe-d751-4c47-833a-e89c4df2fa17"
VAR_3_ID = "2af0fff6-f41f-40c8-a9a9-5becf5310cdd"
VAR_4_ID = "866d2f26-5c6f-4194-856d-514f9fd22cf8"
VAR_5_ID = "a561d4a8-0424-4d69-a5cf-187ad219c527"


def create_model(**overrides: Any) -> OpenAPIModel:
    defaults = {
        "id": MODEL_ID,
        "name": "Test Model",
        "description": "Test model description",
        "status": ModelStatus.SUCCESS,
        "type": ModelType.HISTORICAL,
        "projectId": PROJECT_ID,
        "datasetId": DATASET_ID,
        "variant": "Stepwise GP",
        "stepSize": 3600,
    }
    defaults.update(overrides)
    return OpenAPIModel(**defaults)


def create_project(**overrides: Any) -> OpenAPIProject:
    defaults = {
        "id": PROJECT_ID,
        "name": "Test Project",
        "description": "Test project description",
        "processUnit": ProcessUnitCode.BR,
        "processFormat": ProcessFormatCode.MAMMAL,
    }
    defaults.update(overrides)
    return OpenAPIProject(**defaults)


def create_product(**overrides: Any) -> OpenAPIProduct:
    defaults = {
        "id": PRODUCT_ID,
        "name": "Test Product",
        "code": "TEST_PROD",
        "description": "Test product description",
        "processFormat": ProcessFormatCode.MAMMAL,
    }
    defaults.update(overrides)
    return OpenAPIProduct(**defaults)


def create_variable(**overrides: Any) -> OpenAPIVariable:
    defaults = {
        "id": VARIABLE_ID,
        "name": "Test Variable",
        "code": "TEST_VAR",
        "description": "Test variable description",
        "measurementUnit": "g/L",
        "group": "Process",
        "variantDetails": Variantdetails(),
    }
    defaults.update(overrides)
    return OpenAPIVariable(**defaults)
