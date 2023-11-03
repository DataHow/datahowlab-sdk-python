"""This module contains utility functions used for spectra 
validation and formatting in the SDK
"""

from typing import Optional, Protocol, Union, Dict, List

import numpy as np

from dhl_sdk._utils import (
    Instance,
    PredictRequest,
    PredictResponse,
    validate_list_elements,
)
from dhl_sdk.exceptions import InvalidSpectraException, InvalidInputsException


SpectraData = Union[
    list[list[float]], np.ndarray[(int, int), Union[np.float32, np.float64]]
]
SpectraPrediction = Dict[str, List[float]]


class SpectraModel(Protocol):
    @property
    def inputs(self) -> list[str]:
        ...

    @property
    def outputs(self) -> list[str]:
        ...

    @property
    def spectra_size(self) -> int:
        ...


def validate_prediction_inputs(
    spectra: SpectraData,
    model: SpectraModel,
    inputs: Optional[dict] = None,
) -> tuple[list[list[float]], Optional[dict]]:
    """
    This function validates and makes the necessary formating of the spectra
    and inputs used for prediction. It performs the following validations:

    - Validates if spectra is empty
    - Validates if the number of wavelengths in spectra matches
        the number of wavelengths in the model
    - Validates if the spectra contains None values
    - Validates if the number of inputs matches model inputs
    - Validates if the number of values in each input matches the number of spectra

    Parameters
    ----------
    spectra : Union[list[list[float]], np.ndarray]
        The spectra to be validated
    model : Model
        The model to use for prediction.
    inputs : dict, optional
        A dictionary of input variables and their values, by default None

    Returns
    -------
    list[list[float], dict
        If all validations pass, return the formatted spectra and inputs
        as a tuple.

    Raises
    ------
    InvalidSpectraException
        Exception raised when Spectra is not valid for prediction.
    InvalidInputsException
        Exception raised when Inputs is not valid for prediction.
    """
    # Validate if empty spectra
    n_spectra = len(spectra)
    if n_spectra < 1:
        raise InvalidSpectraException("Empty spectra provided")

    spectra = validate_spectra_format(spectra)

    # Validate number of wavelengths in spectra
    for i, spectrum in enumerate(spectra):
        if len(spectrum) != model.spectra_size:
            raise InvalidSpectraException(
                f"Invalid Spectra: The Number of Wavelengths does not match training data for spectrum number: {i+1}. Expected: {model.spectra_size}, Got: {len(spectrum)}"
            )
        if validate_list_elements(spectrum):
            raise InvalidSpectraException(
                f"Invalid Spectra: The Spectra contains not valid values for spectrum number: {i+1}"
            )

    model_inputs = model.inputs

    if inputs is None:
        if len(model_inputs) > 0:
            raise InvalidInputsException(
                "The model requires inputs, but none were provided."
            )
        return spectra, None

    # validate inputs with spectra inputs (number of lines)
    for key, value in inputs.items():
        if len(value) != n_spectra:
            raise InvalidInputsException(
                f"The Number of values does not match the number of spectra for input: {key}"
            )
        if validate_list_elements(value):
            raise InvalidInputsException(
                f"Invalid Inputs: The Inputs contains not valid values for input: {key}"
            )

    formatted_inputs = format_inputs(inputs, model, model_inputs)

    return spectra, formatted_inputs


def format_inputs(
    inputs: dict, model: SpectraModel, model_inputs: list
) -> Dict[str, List[float]]:
    """
    Format the inputs for a given model.
    Changes the input codes to match the variable ids if
    inputs are provided as codes.

    Parameters
    ----------
    inputs : dict
        A dictionary containing the inputs to format.
    model : Model
        The model to format the inputs for.
    model_inputs : list
        A list of the model inputs.


    Returns
    -------
    dict
        A dictionary containing the formatted inputs.

    Raises
    ------
    InvalidInputsException
        If no matching input is found for a given key.
    """

    model_variables = model.dataset.variables

    input_variables = [
        variable for variable in model_variables if variable.id in model_inputs
    ]

    # validate inputs codes and format for ids
    formatted_inputs = {}
    for key, value in inputs.items():
        for variable in input_variables:
            if variable.matches_key(key):
                formatted_inputs[variable.id] = value
                break
        else:
            correct_inputs = [print(variable) for variable in input_variables]
            raise InvalidInputsException(
                f"No matching Input found for key: {key}. Please select one of the following as inputs: {*correct_inputs,}"
            )

    return formatted_inputs


def validate_spectra_format(spectra: SpectraData) -> list[list[float]]:
    """
    Validates and formats the spectra.

    Parameters
    ----------
    spectra : list or numpy.ndarray
        The spectra to be validated.

    Returns
    -------
    list
        The spectra as a list.

    Raises
    ------
    InvalidSpectraException
        If the spectra is not a list or numpy array.
    """

    if isinstance(spectra, np.ndarray):
        spectra = spectra.tolist()
    elif isinstance(spectra, list):
        pass
    else:
        raise InvalidSpectraException(
            f"Spectra must be a list or numpy array, but got {type(spectra)}"
        )

    return spectra


def convert_to_request(
    spectra: list[list[float]],
    model: SpectraModel,
    inputs: Optional[dict] = None,
    batch_size: int = 50,
) -> list[dict]:
    """
    Convert spectra and inputs to a list of JSON requests.
    Handles big requests by paginating them.

    Parameters
    ----------
    spectra : list[list[float]]
        A list of spectra, where each spectrum is a list of floats.
    model : Model
        The model to use for prediction.
    inputs : dict, optional
        A dictionary of input variables and their values, by default None.
    batch_size : int, optional
        The maximum number of spectra to include in each request, by default 50.

    Returns
    -------
    list[dict]
        A list of JSON requests, where each request contains a list of instances.
    """

    # get number of vars in model from config
    variables = model.dataset.variables
    n_vars = len(variables)
    spectrum_index = model.dataset.get_spectrum_index()

    request_data = []
    # handle pagination
    for i in range(0, len(spectra), batch_size):
        instance = [None] * n_vars
        instance[spectrum_index] = Instance(values=spectra[i : i + batch_size])

        if inputs is not None:
            for input_id, input_values in inputs.items():
                for index, variable in enumerate(variables):
                    if variable.id == input_id:
                        instance[index] = Instance(
                            values=input_values[i : i + batch_size]
                        )
                    break

        json_data = PredictRequest(instances=[instance]).model_dump(by_alias=True)
        request_data.append(json_data)

    return request_data


def format_predictions(
    predictions: List[PredictResponse], model: SpectraModel
) -> SpectraPrediction:
    """Format a list of predictions into a dictionary.

    Parameters
    ----------
    predictions : List[PredictResponse]
        list of predictions from the API.
    model : Model
        Model used for prediction

    Returns
    -------
    Dictionary with predictions where:
        key: variable id
        value: list of predictions
    """
    variables = [var.code for var in model.dataset.variables]

    dic = {}

    for pred in predictions:
        for i, instance in enumerate(pred.instances[0]):
            if instance is not None:
                if variables[i] in dic:
                    dic[variables[i]].extend(instance.values)
                else:
                    dic[variables[i]] = instance.values.copy()

    return dic
