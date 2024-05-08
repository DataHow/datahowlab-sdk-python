"""This module contains generic utility functions used in the SDK
"""

import urllib.parse as urlparse
from datetime import datetime
from functools import reduce
from typing import Optional, Union

import numpy as np
from pydantic import BaseModel, Field, model_validator

from dhl_sdk.crud import Client

Predictions = dict[str, dict[str, list[float]]]

PRODUCTS_URL = "api/db/v2/products"
RECIPES_URL = "api/db/v2/recipes"
FILES_URL = "api/db/v2/files"
EXPERIMENTS_URL = "api/db/v2/experiments"
VARIABLES_URL = "api/db/v2/variables"
GROUPS_URL = "api/db/v2/groups"
PROJECTS_URL = "api/db/v2/projects"
DATASETS_URL = "api/db/v2/datasets"
MODELS_URL = "api/db/v2/pipelineJobs"
TEMPLATES_URL = "api/db/v2/pipelineJobTemplates"
PREDICT_URL = "api/pipeline/v1/predictors"


class VariableGroupCodes:
    """Singleton class to store the variable group codes"""

    _instance = None
    variable_group_codes = {}

    def __new__(cls, client):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(client)
        return cls._instance

    def _initialize(self, client: Client):
        group_codes = {}
        groups = client.get(GROUPS_URL).json()

        for group in groups:
            group_codes[group["name"]] = (group["id"], group["code"])

        self.variable_group_codes = group_codes

    def get_variable_group_codes(self) -> dict[str, tuple[str, str]]:
        """Returns the variable group codes saved in singleton"""
        return self.variable_group_codes


class Instance(BaseModel):
    """Pydantic class representing the Instance
    It is used to type check the request"""

    timestamps: Optional[list[float]] = Field(default=None, alias="timestamps")
    sample_id: Optional[list[str]] = Field(default=None, alias="sampleId")
    values: Union[list[float], list[list[float]]]
    high_values: Optional[Union[list[float], list[list[float]]]] = Field(
        default=None, alias="highValues"
    )
    low_values: Optional[Union[list[float], list[list[float]]]] = Field(
        default=None, alias="lowValues"
    )

    @model_validator(mode="after")
    def generate_sample_ids(self):
        """Generates sample ids if not provided"""
        if self.sample_id is None:
            self.sample_id = [str(i) for i in range(len(self.values))]
        return self


class PredictRequest(BaseModel):
    """Pydantic class representing the expected Predict Request"""

    instances: list[list[Optional[Instance]]]
    metadata: Optional[dict] = None
    config: Optional[dict] = None


class PredictResponse(BaseModel):
    """Pydantic class representing the expected Predict Response"""

    instances: list[list[Optional[Instance]]]


def urljoin(*args) -> str:
    """join url elements together into one url"""
    elements = [
        f"{arg}/" if arg[-1] != "/" and i != len(args) - 1 else arg
        for i, arg in enumerate(args)
    ]
    return reduce(urlparse.urljoin, elements)


def validate_list_elements(arr: list) -> bool:
    """Validates if an array contains non float values"""
    return any(
        not isinstance(item, (float, int))
        or item is None
        or np.isnan(item)
        or np.isinf(item)
        for item in arr
    )


def get_id_list(json_list: list[dict]) -> list[str]:
    """Extracts the id from a list of dictionaries"""
    return [item["id"] for item in json_list]


def is_date_in_format(date_string, date_format):
    """Checks if a date string is in a specific format"""
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False
