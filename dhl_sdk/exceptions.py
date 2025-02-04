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

    def __init__(self, message: str = "The Spectra used for prediction are not valid."):
        self.message = message
        super().__init__(self.message)


class InvalidInputsException(Exception):
    """Exception raised when Inputs used for prediction are not valid"""

    def __init__(self, message: str = "The Inputs used for prediction are not valid."):
        self.message = message
        super().__init__(self.message)


class ModelPredictionException(Exception):
    """Exception raised when Model Prediction fails"""

    def __init__(self, message: str = "Model is not valid for prediction."):
        self.message = message
        super().__init__(self.message)


class InvalidTimestampsException(Exception):
    """Exception raised when timestamps used for prediction are not valid"""

    def __init__(
        self, message: str = "The timestamps used for prediction are not valid."
    ):
        self.message = message
        super().__init__(self.message)


class InvalidVariantException(Exception):
    """Exception raised when variant is not valid"""

    def __init__(self, message: str = "The selected variant is not valid"):
        self.message = message
        super().__init__(self.message)


class InvalidStepsException(Exception):
    """Exception raised when steps used for historical model prediction are not valid"""

    def __init__(
        self, message: str = "The steps used for the prediction are not valid."
    ):
        self.message = message
        super().__init__(self.message)


class InvalidStartingIndexException(Exception):
    """Exception raised when starting index given is not valid"""

    def __init__(self, message: str = "The starting index is not valid."):
        self.message = message
        super().__init__(self.message)


class InvalidConfidenceException(Exception):
    """Exception raised when Model Prediction fails"""

    def __init__(
        self, message: str = "Model Confidence must be a value between 1 and 99"
    ):
        self.message = message
        super().__init__(self.message)


class PredictionRequestException(Exception):
    """Exception raised when prediction request fails"""

    def __init__(self, message: str = "Prediction request failed."):
        self.message = message
        super().__init__(self.message)


class ImportValidationException(Exception):
    """Exception raised when import validation fails"""

    def __init__(self, message: str = "Import validation failed."):
        self.message = message
        super().__init__(self.message)


class NewEntityException(Exception):
    """Exception raised when creating new entity fails"""

    def __init__(self, message: str = "Creating new entity failed."):
        self.message = message
        super().__init__(self.message)
