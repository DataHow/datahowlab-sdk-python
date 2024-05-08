""" New file data importers for DHL SDK"""

# pylint: disable=missing-function-docstring, arguments-differ, protected-access
import csv
from io import StringIO
from typing import Any, Dict, Literal, Protocol

from dhl_sdk._utils import FILES_URL
from dhl_sdk.crud import Client


class File(Protocol):
    """Protocol for file data"""

    type: Literal["run", "spectra"]
    variant: Literal["run", "samples"]
    _data: Dict[str, Any]

    def create_request_body(self) -> Dict[str, Any]:
        pass


class RunFileImporter:
    """Class to import data from a run file"""

    def __init__(self, client: Client):
        self.client = client

    def import_file(self, file: File) -> str:
        """Import the run file to the project and dataset"""

        response = self.client.post(FILES_URL, file.create_request_body())
        file_id = response.json()["id"]

        import_data = {"timeseries": file._data}

        self.client.put(
            f"{FILES_URL}/{file_id}/data",
            data=import_data,
            content_type="application/json",
        )

        return file_id


class SpectraFileImporter:
    """Class to import data from a spectra file"""

    def __init__(self, client: Client):
        self.client = client

    def import_file(self, file: File) -> tuple[str, str]:
        """Import the spectra file to the project and dataset"""

        # Create Spectra file
        response = self.client.post(FILES_URL, self._file_spectra_body(file))
        spectra_file_id = response.json()["id"]

        import_data = self._spectra_data(file._data, file.variant)

        self.client.put(
            f"{FILES_URL}/{spectra_file_id}/data",
            data=import_data,
            content_type="text/csv",
        )

        # Create Targets file
        response = self.client.post(FILES_URL, self._file_vars_body(file))
        vars_file_id = response.json()["id"]

        import_data = self._variables_data(file._data, file.variant)

        self.client.put(
            f"{FILES_URL}/{vars_file_id}/data",
            data=import_data,
            content_type="application/json",
        )

        return (spectra_file_id, vars_file_id)

    def _file_spectra_body(self, file: File) -> Dict[str, Any]:
        """Create the request body for the spectra file"""
        return file.create_request_body()

    def _file_vars_body(self, file: File) -> Dict[str, Any]:
        """Create the request body for the targets file"""

        file_dict = file.model_dump(
            exclude_none=True,
            by_alias=True,
            include={"name": True, "description": True},
        )

        if file.variant == "run":
            file_dict["type"] = "runData"
        elif file.variant == "samples":
            file_dict["type"] = "sampleData"

        return file_dict

    def _spectra_data(self, data: dict[str, Any], variant: str = "run") -> str:
        """Create the request body for the spectra data"""

        spectra_data = data["spectra"]

        if variant == "run":
            sample_id = "timestamps"
        elif variant == "samples":
            sample_id = "sampleId"
        else:
            raise ValueError(f"Invalid variant: {variant}")

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)

        # Write data rows
        for timestamp, value_list in zip(
            spectra_data[sample_id], spectra_data["values"]
        ):
            csv_writer.writerow([timestamp] + value_list)

        csv_string = csv_data.getvalue()
        csv_data.close()

        return csv_string

    def _variables_data(self, data: dict[str, Any], variant: str = "run") -> dict:
        """Create the request body for the variables data"""

        data.pop("spectra", None)

        variables_data = data

        if variables_data is None:
            raise ValueError("No spectra data found")

        if variant == "run":
            import_data = {"timeseries": variables_data}
        elif variant == "samples":
            import_data = {"samples": variables_data}
        else:
            raise ValueError(f"Invalid variant: {variant}")

        return import_data
