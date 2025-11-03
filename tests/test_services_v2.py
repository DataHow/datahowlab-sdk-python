"""Unit tests for dhl_sdk.services module

Tests FileService and DataFormatService in isolation using mocks.
"""

from unittest.mock import Mock

from dhl_sdk.services import DataFormatService, FileService
from dhl_sdk.types import SpectraData, TimeseriesData


class TestFileService:
    """Unit tests for FileService class"""

    def test_upload_json_file(self):
        """Test JSON file upload creates metadata and uploads data"""
        # Setup mock request function
        mock_request = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "file-123"}
        mock_request.return_value = mock_response

        service = FileService(mock_request, "/api/files")

        # Upload JSON file
        file_id = service.upload_json_file(
            "test_data", "runData", {"timeseries": {"VAR1": {}}}
        )

        # Verify file_id returned
        assert file_id == "file-123"

        # Verify two requests made: POST metadata + PUT data
        assert mock_request.call_count == 2

        # Verify first call (POST metadata)
        first_call = mock_request.call_args_list[0]
        assert first_call[0][0] == "POST"  # method
        assert first_call[0][1] == "/api/files"  # url
        assert first_call[1]["json_data"]["name"] == "test_data"
        assert first_call[1]["json_data"]["type"] == "runData"

        # Verify second call (PUT data)
        second_call = mock_request.call_args_list[1]
        assert second_call[0][0] == "PUT"
        assert second_call[0][1] == "/api/files/file-123/data"
        assert second_call[1]["json_data"] == {"timeseries": {"VAR1": {}}}

    def test_upload_csv_file(self):
        """Test CSV file upload"""
        mock_request = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "file-456"}
        mock_request.return_value = mock_response

        service = FileService(mock_request, "/api/files")

        # Upload CSV file
        csv_data = "timestamp,value\n1,42\n2,43\n"
        file_id = service.upload_csv_file("spectra", "runSpectra", csv_data)

        assert file_id == "file-456"
        assert mock_request.call_count == 2

        # Verify CSV data passed as raw string
        second_call = mock_request.call_args_list[1]
        assert second_call[1]["data"] == csv_data
        assert second_call[1]["content_type"] == "text/csv"

    def test_upload_file_generic(self):
        """Test generic upload_file method"""
        mock_request = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "file-789"}
        mock_request.return_value = mock_response

        service = FileService(mock_request, "/api/files")

        # Upload with generic method
        file_id = service.upload_file(
            name="custom",
            file_type="sampleData",
            data={"key": "value"},
            content_type="application/json",
        )

        assert file_id == "file-789"

    def test_download_file(self):
        """Test file download"""
        mock_request = Mock()
        mock_response = Mock()
        mock_response.text = "file contents"
        mock_request.return_value = mock_response

        service = FileService(mock_request, "/api/files")

        # Download file
        response = service.download_file("file-123")

        assert response.text == "file contents"
        mock_request.assert_called_once_with("GET", "/api/files/file-123/data")

    def test_upload_with_empty_name(self):
        """Test upload with empty name still works"""
        mock_request = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "file-empty"}
        mock_request.return_value = mock_response

        service = FileService(mock_request, "/api/files")

        file_id = service.upload_json_file("", "runData", {})

        assert file_id == "file-empty"
        # Verify empty name was passed through
        first_call = mock_request.call_args_list[0]
        assert first_call[1]["json_data"]["name"] == ""


class TestDataFormatService:
    """Unit tests for DataFormatService class"""

    def test_format_spectra_to_csv_with_timestamps(self):
        """Test CSV formatting with timestamps"""
        service = DataFormatService()

        spectra = SpectraData(
            timestamps=[1735689600, 1735689700],
            values=[[1.0, 2.0, 3.0], [1.1, 2.1, 3.1]],
        )

        csv_str = service.format_spectra_to_csv(spectra)

        # Verify CSV format (strip \r from Windows-style line endings)
        lines = [line.rstrip("\r") for line in csv_str.strip().split("\n")]
        assert len(lines) == 2

        # First row
        assert lines[0] == "1735689600,1.0,2.0,3.0"
        # Second row
        assert lines[1] == "1735689700,1.1,2.1,3.1"

    def test_format_spectra_to_csv_with_sample_ids(self):
        """Test CSV formatting with sample IDs"""
        service = DataFormatService()

        spectra = SpectraData(
            sample_ids=["sample1", "sample2"],
            values=[[10.0, 20.0], [11.0, 21.0]],
        )

        csv_str = service.format_spectra_to_csv(spectra)

        lines = [line.rstrip("\r") for line in csv_str.strip().split("\n")]
        assert len(lines) == 2
        assert lines[0] == "sample1,10.0,20.0"
        assert lines[1] == "sample2,11.0,21.0"

    def test_parse_csv_to_spectra_run_variant(self):
        """Test CSV parsing for run variant (timestamps)"""
        service = DataFormatService()

        csv_text = "1735689600,1.0,2.0\n1735689700,1.1,2.1\n"

        result = service.parse_csv_to_spectra(csv_text, variant="run")

        assert "timestamps" in result
        assert result["timestamps"] == ["1735689600", "1735689700"]
        assert result["values"] == [["1.0", "2.0"], ["1.1", "2.1"]]

    def test_parse_csv_to_spectra_sample_variant(self):
        """Test CSV parsing for sample variant (sample IDs)"""
        service = DataFormatService()

        csv_text = "sample1,10.0,20.0\nsample2,11.0,21.0\n"

        result = service.parse_csv_to_spectra(csv_text, variant="sample")

        assert "sampleId" in result
        assert result["sampleId"] == ["sample1", "sample2"]
        assert result["values"] == [["10.0", "20.0"], ["11.0", "21.0"]]

    def test_parse_csv_to_spectra_empty(self):
        """Test CSV parsing with empty string"""
        service = DataFormatService()

        result = service.parse_csv_to_spectra("", variant="run")

        assert result == {}

    def test_parse_csv_to_spectra_single_row(self):
        """Test CSV parsing with single data row"""
        service = DataFormatService()

        csv_text = "1735689600,42.0,43.0,44.0\n"

        result = service.parse_csv_to_spectra(csv_text, variant="run")

        assert len(result["timestamps"]) == 1
        assert result["timestamps"][0] == "1735689600"
        assert result["values"][0] == ["42.0", "43.0", "44.0"]

    def test_format_timeseries_to_json(self):
        """Test timeseries JSON formatting"""
        service = DataFormatService()

        timeseries_dict = {
            "TEMP": TimeseriesData(timestamps=[0, 60], values=[25.0, 26.0]),
            "PH": TimeseriesData(timestamps=[0, 60], values=[7.0, 7.1]),
        }

        result = service.format_timeseries_to_json(timeseries_dict)

        assert "timeseries" in result
        assert "TEMP" in result["timeseries"]
        assert "PH" in result["timeseries"]

        # Verify TEMP data
        assert result["timeseries"]["TEMP"]["timestamps"] == [0, 60]
        assert result["timeseries"]["TEMP"]["values"] == [25.0, 26.0]

        # Verify PH data
        assert result["timeseries"]["PH"]["timestamps"] == [0, 60]
        assert result["timeseries"]["PH"]["values"] == [7.0, 7.1]

    def test_format_timeseries_to_json_empty(self):
        """Test timeseries formatting with empty dict"""
        service = DataFormatService()

        result = service.format_timeseries_to_json({})

        assert result == {"timeseries": {}}

    def test_format_timeseries_to_json_single_variable(self):
        """Test timeseries formatting with single variable"""
        service = DataFormatService()

        timeseries_dict = {
            "VAR1": TimeseriesData(timestamps=[0, 1, 2], values=[1.0, 2.0, 3.0])
        }

        result = service.format_timeseries_to_json(timeseries_dict)

        assert len(result["timeseries"]) == 1
        assert result["timeseries"]["VAR1"]["timestamps"] == [0, 1, 2]
        assert result["timeseries"]["VAR1"]["values"] == [1.0, 2.0, 3.0]


class TestFileServiceEdgeCases:
    """Edge case tests for FileService"""

    def test_upload_large_json_data(self):
        """Test uploading large JSON data"""
        mock_request = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "file-large"}
        mock_request.return_value = mock_response

        service = FileService(mock_request, "/api/files")

        # Create large data structure
        large_data = {
            "timeseries": {f"VAR{i}": {"timestamps": list(range(1000)), "values": list(range(1000))} for i in range(100)}
        }

        file_id = service.upload_json_file("large", "runData", large_data)

        assert file_id == "file-large"
        # Verify large data was passed through
        second_call = mock_request.call_args_list[1]
        assert len(second_call[1]["json_data"]["timeseries"]) == 100

    def test_upload_with_special_characters_in_name(self):
        """Test upload with special characters in filename"""
        mock_request = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "file-special"}
        mock_request.return_value = mock_response

        service = FileService(mock_request, "/api/files")

        # Name with special characters
        file_id = service.upload_json_file(
            "file with spaces & symbols!@#", "runData", {}
        )

        assert file_id == "file-special"
        first_call = mock_request.call_args_list[0]
        assert first_call[1]["json_data"]["name"] == "file with spaces & symbols!@#"


class TestDataFormatServiceEdgeCases:
    """Edge case tests for DataFormatService"""

    def test_parse_csv_with_trailing_newlines(self):
        """Test CSV parsing handles trailing newlines"""
        service = DataFormatService()

        csv_text = "1,1.0,2.0\n2,3.0,4.0\n\n\n"

        result = service.parse_csv_to_spectra(csv_text, variant="run")

        # Should ignore empty lines
        assert len(result["timestamps"]) == 2
        assert result["timestamps"] == ["1", "2"]

    def test_format_timeseries_preserves_order(self):
        """Test timeseries formatting preserves dict order"""
        service = DataFormatService()

        # Python 3.7+ guarantees dict order
        timeseries_dict = {
            "VAR3": TimeseriesData(timestamps=[0], values=[3.0]),
            "VAR1": TimeseriesData(timestamps=[0], values=[1.0]),
            "VAR2": TimeseriesData(timestamps=[0], values=[2.0]),
        }

        result = service.format_timeseries_to_json(timeseries_dict)

        keys = list(result["timeseries"].keys())
        assert keys == ["VAR3", "VAR1", "VAR2"]

    def test_parse_csv_with_single_wavelength(self):
        """Test CSV parsing with single wavelength per spectrum"""
        service = DataFormatService()

        csv_text = "1,42.0\n2,43.0\n"

        result = service.parse_csv_to_spectra(csv_text, variant="run")

        assert result["timestamps"] == ["1", "2"]
        assert result["values"] == [["42.0"], ["43.0"]]
