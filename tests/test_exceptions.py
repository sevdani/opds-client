"""Tests for OPDS exceptions."""

from opds_client.opds2.exceptions import (
    InvalidOPDSFeedError,
    OPDSClientError,
    OPDSHTTPError,
    OPDSNavigationError,
    OPDSParseError,
    OPDSRetryError,
    OPDSValidationError,
    SearchError,
)


class TestOPDSExceptions:
    """Tests for OPDS exceptions."""

    def test_base_exception(self):
        """Test base exception."""
        exc = OPDSClientError("Base error")
        assert str(exc) == "Base error"

    def test_parse_error(self):
        """Test parse error."""
        original = ValueError("Original error")
        exc = OPDSParseError("Parse error", original)
        assert str(exc) == "Parse error"
        assert exc.original_error is original

    def test_validation_error(self):
        """Test validation error."""
        exc = OPDSValidationError("Validation error")
        assert str(exc) == "Validation error"

    def test_validation_error_with_details(self):
        """Test validation error with details."""
        exc = OPDSValidationError("Validation error", ["Error 1", "Error 2"])
        assert exc.validation_errors == ["Error 1", "Error 2"]

    def test_invalid_feed_error(self):
        """Test invalid feed error."""
        exc = InvalidOPDSFeedError("Invalid feed")
        assert isinstance(exc, OPDSValidationError)

    def test_http_error(self):
        """Test HTTP error."""
        exc = OPDSHTTPError("HTTP error", 404, "https://example.com", "body")
        assert exc.status_code == 404
        assert exc.url == "https://example.com"
        assert exc.response_body == "body"

    def test_navigation_error(self):
        """Test navigation error."""
        exc = OPDSNavigationError("Navigation error")
        assert str(exc) == "Navigation error"

    def test_retry_error(self):
        """Test retry error."""
        exc = OPDSRetryError("Retry error", retry_after=5)
        assert exc.retry_after == 5

    def test_retry_error_no_retry_after(self):
        """Test retry error without retry_after."""
        exc = OPDSRetryError("Retry error")
        assert exc.retry_after is None

    def test_search_error(self):
        """Test search error."""
        exc = SearchError("Search error")
        assert str(exc) == "Search error"

    def test_exception_inheritance(self):
        """Test exception inheritance."""
        assert issubclass(OPDSParseError, OPDSClientError)
        assert issubclass(OPDSValidationError, OPDSClientError)
        assert issubclass(InvalidOPDSFeedError, OPDSValidationError)
        assert issubclass(OPDSHTTPError, OPDSClientError)
        assert issubclass(OPDSNavigationError, OPDSClientError)
        assert issubclass(OPDSRetryError, OPDSClientError)
        assert issubclass(SearchError, OPDSClientError)
