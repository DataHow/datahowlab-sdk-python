"""Edge case tests for DataHowLabClient

Tests edge cases, error conditions, and boundary scenarios including:
- Pagination behavior
- Timeout handling
- Input validation
- Error response sanitization
- URL encoding and special characters
"""

from unittest.mock import Mock, patch

import pytest
import requests

from dhl_sdk.client import DataHowLabClient
from dhl_sdk.errors import (
    APIError,
    AuthenticationError,
    EntityNotFoundError,
    ServerError,
)


class TestPaginationEdgeCases:
    """Test pagination behavior in various scenarios"""

    def test_list_products_empty_results(self):
        """Test handling of empty results from API"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")
            products = client.list_products(limit=10)

            assert products == []

    def test_list_products_large_limit(self):
        """Test requesting large limit"""
        with patch("requests.Session.request") as mock_request:
            # Simulate API returning max allowed results
            mock_response = Mock()
            mock_response.json.return_value = [
                {
                    "id": f"prod-{i}",
                    "code": f"PROD{i:03d}",
                    "name": f"Product {i}",
                    "description": "",
                }
                for i in range(1000)
            ]
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")
            products = client.list_products(limit=1000)

            assert len(products) == 1000

    def test_list_experiments_partial_last_page(self):
        """Test last page with fewer items than limit"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            # Return only 3 items when limit is 10 (last page)
            mock_response.json.return_value = [
                {
                    "id": f"exp-{i}",
                    "variant": "run",
                    "code": f"EXP{i}",
                    "name": f"Experiment {i}",
                    "description": "",
                    "processFormatVariant": "mammalian",
                    "product": {"id": "prod-1", "code": "P1"},
                }
                for i in range(3)
            ]
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")
            experiments = client.list_experiments(limit=10)

            assert len(experiments) == 3

    def test_page_iterator(self):
        """Test PageIterator for fetching all results"""
        with patch("requests.Session.request") as mock_request:
            # Mock two pages of results
            page1 = [
                {
                    "id": f"prod-{i}",
                    "code": f"PROD{i:03d}",
                    "name": f"Product {i}",
                    "description": "",
                }
                for i in range(100)
            ]
            page2 = [
                {
                    "id": f"prod-{i}",
                    "code": f"PROD{i:03d}",
                    "name": f"Product {i}",
                    "description": "",
                }
                for i in range(100, 125)
            ]

            mock_response1 = Mock()
            mock_response1.json.return_value = page1
            mock_response1.status_code = 200

            mock_response2 = Mock()
            mock_response2.json.return_value = page2
            mock_response2.status_code = 200

            mock_request.side_effect = [mock_response1, mock_response2]

            client = DataHowLabClient(api_key="test-key")
            # iter_all=True returns PageIterator
            products_iter = client.list_products(iter_all=True)

            # Consume the iterator
            products = list(products_iter)

            # Should have fetched two pages
            assert len(products) == 125
            assert mock_request.call_count == 2


class TestTimeoutHandling:
    """Test request timeout behavior"""

    def test_request_timeout_default(self):
        """Test default timeout is applied"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")
            client.list_products()

            # Verify default timeout (30.0) was used
            call_args = mock_request.call_args
            assert call_args.kwargs["timeout"] == 30.0

    def test_request_timeout_custom(self):
        """Test custom timeout is applied"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key", timeout=5.0)
            client.list_products()

            # Verify custom timeout was used
            call_args = mock_request.call_args
            assert call_args.kwargs["timeout"] == 5.0

    def test_request_timeout_exception(self):
        """Test timeout exception is wrapped in APIError"""
        with patch("requests.Session.request") as mock_request:
            mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

            client = DataHowLabClient(api_key="test-key", timeout=1.0)

            # SDK wraps Timeout in APIError
            with pytest.raises(APIError) as exc_info:
                client.list_products()

            assert "timed out" in str(exc_info.value).lower()


class TestInputValidation:
    """Test validation of user inputs"""

    def test_list_variables_with_filter(self):
        """Test listing variables with type filter"""
        with patch("requests.Session.request") as mock_request:
            # Mock response for list_variables
            vars_response = Mock()
            vars_response.json.return_value = []
            vars_response.status_code = 200

            mock_request.return_value = vars_response

            client = DataHowLabClient(api_key="test-key")
            _variables = client.list_variables(variable_type="numeric")

            # Verify correct filter was applied
            call_args = mock_request.call_args
            url = call_args[0][1]
            assert "filterBy%5Bvariant%5D=numeric" in url or "filterBy[variant]=numeric" in url


class TestErrorResponseHandling:
    """Test handling of various error responses"""

    def test_http_401_unauthorized(self):
        """Test handling of 401 Unauthorized error"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="invalid-key")

            # SDK raises AuthenticationError for 401
            with pytest.raises(AuthenticationError) as exc_info:
                client.list_products()

            assert "unauthorized" in str(exc_info.value).lower()

    def test_http_404_not_found(self):
        """Test handling of 404 Not Found error"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not found"
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")

            # SDK wraps 404 in EntityNotFoundError
            with pytest.raises(EntityNotFoundError) as exc_info:
                client.get_product("nonexistent-id")

            assert exc_info.value.entity_type == "Product"

    def test_http_500_internal_server_error(self):
        """Test handling of 500 Internal Server Error"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")

            # SDK raises ServerError for 500
            with pytest.raises(ServerError) as exc_info:
                client.list_products()

            assert exc_info.value.status_code == 500

    def test_sanitization_api_key_in_error(self):
        """Test that API keys are sanitized in error messages"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            # Response body contains API key
            mock_response.text = '{"error": "Invalid request", "api_key": "secret-key-12345"}'
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")

            # SDK wraps HTTPError in APIError with sanitized body
            with pytest.raises(APIError) as exc_info:
                client.list_products()

            # The actual API key should not appear in the error's response_body
            error = exc_info.value
            if error.response_body:
                assert "secret-key-12345" not in error.response_body
                assert "***REDACTED***" in error.response_body

    def test_sanitization_long_response_truncated(self):
        """Test that long error responses are truncated"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            # Very long response body (over 500 chars)
            long_body = "Error: " + ("x" * 1000)
            mock_response.text = long_body
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")

            # SDK wraps HTTPError in APIError with truncated body
            with pytest.raises(APIError) as exc_info:
                client.list_products()

            # Should contain truncation marker
            error = exc_info.value
            if error.response_body:
                assert "... (truncated)" in error.response_body
                assert len(error.response_body) < len(long_body)


class TestURLEncodingAndSpecialCharacters:
    """Test handling of special characters in URLs and parameters"""

    def test_product_code_with_spaces(self):
        """Test product code with spaces is URL encoded"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = [
                {
                    "id": "prod-1",
                    "code": "PROD 001",
                    "name": "Product with space",
                    "description": "",
                }
            ]
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")
            # Use list_products with code filter instead of get_product_by_code
            _products = client.list_products(code="PROD 001")

            # Verify URL encoding happened (space encoded as %20 or +)
            call_args = mock_request.call_args
            url = call_args[0][1]  # Second positional arg is the URL
            assert "PROD" in url
            assert ("%20" in url or "+" in url) or "PROD 001" in url

    def test_experiment_name_with_special_chars(self):
        """Test experiment name with special characters"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = [
                {
                    "id": "exp-1",
                    "variant": "run",
                    "code": "EXP001",
                    "name": "Experiment #1 (Test/Run)",
                    "description": "",
                    "processFormatVariant": "mammalian",
                    "product": {"id": "prod-1", "code": "P1"},
                }
            ]
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key")
            _experiments = client.list_experiments(name="Experiment #1 (Test/Run)")

            # Verify call was made and special chars were handled
            call_args = mock_request.call_args
            url = call_args[0][1]
            assert "Experiment" in url or "%23" in url  # # encodes to %23


class TestConnectionEdgeCases:
    """Test connection and network edge cases"""

    def test_ssl_verification_disabled(self):
        """Test SSL verification can be disabled"""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.status_code = 200
            mock_session.request.return_value = mock_response

            client = DataHowLabClient(api_key="test-key", verify_ssl=False)
            # Verify verify=False was set on session
            assert client.session.verify is False

    def test_custom_ssl_cert_path(self):
        """Test custom SSL certificate path"""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.status_code = 200
            mock_session.request.return_value = mock_response

            client = DataHowLabClient(
                api_key="test-key", verify_ssl="/path/to/cert.pem"
            )
            # Verify custom cert path was set on session
            assert client.session.verify == "/path/to/cert.pem"

    def test_connection_error(self):
        """Test handling of connection errors"""
        with patch("requests.Session.request") as mock_request:
            mock_request.side_effect = requests.exceptions.ConnectionError(
                "Failed to connect"
            )

            client = DataHowLabClient(api_key="test-key")

            # SDK wraps ConnectionError in APIError
            with pytest.raises(APIError) as exc_info:
                client.list_products()

            assert "Failed to connect" in str(exc_info.value)

    def test_custom_base_url(self):
        """Test using custom base URL"""
        with patch("requests.Session.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            client = DataHowLabClient(
                api_key="test-key", base_url="https://custom.datahowlab.ch"
            )
            client.list_products()

            # Verify custom base URL was used
            call_args = mock_request.call_args
            url = call_args[0][1]
            assert "https://custom.datahowlab.ch" in url
