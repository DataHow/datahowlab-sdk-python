"""
Exceptions Module

This module defines custom exception classes for use throughout the project.

Exceptions:
    - InvalidSpectraException: Exception raised when spectra used for prediction 
      are not valid
    - InvalidInputsException: Exception raised when Inputs used for prediction
      are not valid
    - ModelPredictionException: Exception raised when Model Prediction fails
    - InvalidTimestampsException: Exception raised when timestamps used for 
      prediction are not valid
    - InvalidStepsException: Exception raised when steps used for historical 
      model prediction are not valid
    - PredictionRequestException: Exception raised when prediction request fails
    - ImportValidationException: Exception raised when import validation fails
    - NewEntityException: Exception raised when creating new entity fails
"""


class InvalidSpectraException(Exception):
    """Exception raised when spectra used for prediction are not valid"""

    def __init__(self, message="The Spectra used for prediction are not valid."):
        self.message = message
        super().__init__(self.message)


class InvalidInputsException(Exception):
    """Exception raised when Inputs used for prediction are not valid"""

    def __init__(self, message="The Inputs used for prediction are not valid."):
        self.message = message
        super().__init__(self.message)


class ModelPredictionException(Exception):
    """Exception raised when Model Prediction fails"""

    def __init__(self, message="Model is not valid for prediction."):
        self.message = message
        super().__init__(self.message)


class InvalidTimestampsException(Exception):
    """Exception raised when timestamps used for prediction are not valid"""

    def __init__(self, message="The timestamps used for prediction are not valid."):
        self.message = message
        super().__init__(self.message)


class InvalidStepsException(Exception):
    """Exception raised when steps used for historical model prediction are not valid"""

    def __init__(self, message="The steps used for the prediction are not valid."):
        self.message = message
        super().__init__(self.message)


class InvalidStartingIndexException(Exception):
    """Exception raised when starting index given is not valid"""

    def __init__(self, message="The starting index is not valid."):
        self.message = message
        super().__init__(self.message)


class PredictionRequestException(Exception):
    """Exception raised when prediction request fails"""

    def __init__(self, message="Prediction request failed."):
        self.message = message
        super().__init__(self.message)


class ImportValidationException(Exception):
    """Exception raised when import validation fails"""

    def __init__(self, message="Import validation failed."):
        self.message = message
        super().__init__(self.message)


class NewEntityException(Exception):
    """Exception raised when creating new entity fails"""

    def __init__(self, message="Creating new entity failed."):
        self.message = message
        super().__init__(self.message)
