"""This module contains generic utility functions used in the SDK
"""

import urllib.parse as urlparse
from datetime import datetime
from functools import reduce
from typing import Optional, Union

import numpy as np
from pydantic import BaseModel, Field, model_validator

from dhl_sdk._constants import GROUPS_URL
from dhl_sdk.crud import Client
from dhl_sdk.exceptions import InvalidConfidenceException

Predictions = dict[str, dict[str, list[float]]]


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
    Used to type check the request"""

    timestamps: Optional[list[int]] = Field(default=None, alias="timestamps")
    sample_id: Optional[list[str]] = Field(default=None, alias="sampleId")
    steps: Optional[list[int]] = Field(default=None, alias="steps")
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


class PredictionConfig(BaseModel):
    """Prediction configurations"""

    starting_index: int = Field(alias="startingIndex", default=0)
    high_values_percentile: float = Field(alias="highValuesPercentile", default=90)
    low_values_percentile: float = Field(alias="lowValuesPercentile", default=10)

    @staticmethod
    def new(model_confidence: float, starting_index: int = 0) -> "PredictionConfig":
        """Create a new Prediction Configuration object"""
        if not 1.0 < model_confidence < 99.0:
            raise InvalidConfidenceException()

        high_value = 50.0 + model_confidence / 2
        low_value = 50.0 - model_confidence / 2

        return PredictionConfig(
            startingIndex=starting_index,
            highValuesPercentile=high_value,
            lowValuesPercentile=low_value,
        )


class PredictionRequest(BaseModel):
    """Pydantic class representing the expected Predict Request"""

    instances: list[list[Optional[Instance]]]
    metadata: Optional[dict] = None
    config: Optional[PredictionConfig] = None


class PredictionResponse(BaseModel):
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
