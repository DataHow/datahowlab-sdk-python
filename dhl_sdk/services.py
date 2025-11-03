"""Service classes for SDK operations

This module contains service classes that handle specific concerns like file operations
and data formatting, reducing complexity in the main client class.
"""

import csv
from collections.abc import Callable
from io import StringIO
from typing import Any

import requests


class FileService:
    """Service for handling file upload and download operations

    This service encapsulates all file-related operations including:
    - File metadata creation
    - File content upload
    - File content download
    - CSV and JSON formatting

    Examples:
        >>> service = FileService(request_func=client._request)
        >>> file_id = service.upload_json_file("data", "runData", {"key": "value"})
        >>> data = service.download_json_file(file_id)
    """

    def __init__(self, request_func: Callable, files_url: str):
        """Initialize FileService

        Args:
            request_func: Function to make HTTP requests (typically client._request)
            files_url: Base URL for file operations (e.g., "/api/db/v2/files")
        """
        self._request = request_func
        self.files_url = files_url

    def upload_file(
        self,
        name: str,
        file_type: str,
        data: dict | str,
        content_type: str,
    ) -> str:
        """Upload a file to the API

        This is a two-step process:
        1. POST /files to create file metadata
        2. PUT /files/{id}/data to upload content

        Args:
            name: File name
            file_type: File type (e.g., "runData", "runSpectra", "sampleData")
            data: File content (dict for JSON, str for CSV)
            content_type: MIME type ("application/json" or "text/csv")

        Returns:
            File ID

        Examples:
            >>> # Upload JSON file
            >>> file_id = service.upload_file(
            ...     name="experiment_data",
            ...     file_type="runData",
            ...     data={"timeseries": {...}},
            ...     content_type="application/json"
            ... )
            >>>
            >>> # Upload CSV file
            >>> csv_data = "timestamp,value\\n1,42\\n2,43\\n"
            >>> file_id = service.upload_file(
            ...     name="spectra",
            ...     file_type="runSpectra",
            ...     data=csv_data,
            ...     content_type="text/csv"
            ... )
        """
        # Step 1: Create file metadata
        file_body = {
            "name": name,
            "description": "",
            "type": file_type,
        }
        response = self._request("POST", self.files_url, json_data=file_body)
        file_id = response.json()["id"]

        # Step 2: Upload file data
        if content_type == "application/json":
            self._request("PUT", f"{self.files_url}/{file_id}/data", json_data=data)
        else:  # text/csv or other raw content
            self._request(
                "PUT",
                f"{self.files_url}/{file_id}/data",
                data=data,
                content_type=content_type,
            )

        return file_id

    def upload_json_file(
        self,
        name: str,
        file_type: str,
        data: dict,
    ) -> str:
        """Convenience method to upload JSON file

        Args:
            name: File name
            file_type: File type
            data: JSON data as dictionary

        Returns:
            File ID
        """
        return self.upload_file(name, file_type, data, "application/json")

    def upload_csv_file(
        self,
        name: str,
        file_type: str,
        data: str,
    ) -> str:
        """Convenience method to upload CSV file

        Args:
            name: File name
            file_type: File type
            data: CSV data as string

        Returns:
            File ID
        """
        return self.upload_file(name, file_type, data, "text/csv")

    def download_file(self, file_id: str) -> requests.Response:
        """Download file content

        Args:
            file_id: File ID to download

        Returns:
            Response object with file content
        """
        return self._request("GET", f"{self.files_url}/{file_id}/data")


class DataFormatService:
    """Service for formatting data for API requests

    This service handles conversion between SDK types and API formats:
    - CSV formatting for spectra data
    - JSON structuring for timeseries data
    - Data parsing from API responses

    Examples:
        >>> service = DataFormatService()
        >>> csv_str = service.format_spectra_to_csv(spectra_data)
        >>> json_data = service.format_timeseries_to_json(timeseries_dict)
    """

    @staticmethod
    def format_spectra_to_csv(spectra: Any) -> str:
        """Format spectra data as CSV string

        CSV format: Each row contains [timestamp/sample_id, wavelength1, wavelength2, ...]

        Args:
            spectra: SpectraData object with timestamps/sample_ids and values

        Returns:
            CSV string

        Examples:
            >>> from dhl_sdk.types import SpectraData
            >>> spectra = SpectraData(
            ...     timestamps=[1735689600, 1735689700],
            ...     values=[[1.0, 2.0, 3.0], [1.1, 2.1, 3.1]]
            ... )
            >>> csv_str = DataFormatService.format_spectra_to_csv(spectra)
            >>> print(csv_str)
            1735689600,1.0,2.0,3.0
            1735689700,1.1,2.1,3.1
        """
        output = StringIO()
        writer = csv.writer(output)

        # Get IDs (either timestamps or sample_ids)
        ids = spectra.timestamps or spectra.sample_ids

        # Write rows: [id, wavelength1, wavelength2, ...]
        for i, spectrum_values in enumerate(spectra.values):
            row = [ids[i], *spectrum_values]
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def parse_csv_to_spectra(csv_text: str, variant: str) -> dict:
        """Parse CSV text into spectra data structure

        Args:
            csv_text: Raw CSV string
            variant: Experiment variant ("run" or "sample")

        Returns:
            Dict with structure: {id_key: [...], "values": [[...]]}
            where id_key is "timestamps" for run or "sampleId" for sample

        Examples:
            >>> csv_text = "1735689600,1.0,2.0\\n1735689700,1.1,2.1\\n"
            >>> data = DataFormatService.parse_csv_to_spectra(csv_text, "run")
            >>> data["timestamps"]
            ['1735689600', '1735689700']
            >>> data["values"]
            [['1.0', '2.0'], ['1.1', '2.1']]
        """
        csv_data = list(csv.reader(StringIO(csv_text)))

        # Filter out empty rows (handles trailing newlines)
        csv_data = [row for row in csv_data if row]

        if not csv_data:
            return {}

        # CSV format: timestamp/sample_id, wavelength1, wavelength2, ...
        ids = [row[0] for row in csv_data]
        spectra_values = [row[1:] for row in csv_data]

        # Determine ID type based on experiment variant
        id_key = "timestamps" if variant == "run" else "sampleId"

        return {id_key: ids, "values": spectra_values}

    @staticmethod
    def format_timeseries_to_json(timeseries: dict) -> dict:
        """Format timeseries data for JSON upload

        Args:
            timeseries: Dict mapping variable code to TimeseriesData

        Returns:
            Dict with structure: {"timeseries": {code: {"timestamps": [...], "values": [...]}}}

        Examples:
            >>> from dhl_sdk.types import TimeseriesData
            >>> data = {
            ...     "TEMP": TimeseriesData(timestamps=[0, 60], values=[25.0, 26.0]),
            ...     "PH": TimeseriesData(timestamps=[0, 60], values=[7.0, 7.1])
            ... }
            >>> json_data = DataFormatService.format_timeseries_to_json(data)
            >>> json_data["timeseries"]["TEMP"]
            {"timestamps": [0, 60], "values": [25.0, 26.0]}
        """
        return {
            "timeseries": {
                code: {
                    "timestamps": ts.timestamps,
                    "values": ts.values,
                }
                for code, ts in timeseries.items()
            }
        }
