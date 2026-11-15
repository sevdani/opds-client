"""Custom exceptions for OPDS client."""

from __future__ import annotations


class OPDSClientError(Exception):
    """Base exception for OPDS client errors."""

    pass


class OPDSParseError(OPDSClientError):
    """Error parsing OPDS JSON."""

    def __init__(self, message: str, original_error: Exception | None = None):
        """Initialize OPDSParseError.

        Args:
            message: Error message.
            original_error: Original exception that caused this error.
        """
        super().__init__(message)
        self.original_error = original_error


class OPDSValidationError(OPDSClientError):
    """Error validating OPDS data against schema."""

    def __init__(self, message: str, validation_errors: list[str] | None = None):
        """Initialize OPDSValidationError.

        Args:
            message: Error message.
            validation_errors: List of validation error details.
        """
        super().__init__(message)
        self.validation_errors = validation_errors or []


class InvalidOPDSFeedError(OPDSValidationError):
    """Feed doesn't meet OPDS 2.0 requirements."""

    pass


class OPDSHTTPError(OPDSClientError):
    """HTTP error from OPDS server."""

    def __init__(
        self,
        message: str,
        status_code: int,
        url: str,
        response_body: str | None = None,
    ):
        """Initialize OPDSHTTPError.

        Args:
            message: Error message.
            status_code: HTTP status code.
            url: URL that caused the error.
            response_body: Optional response body for debugging.
        """
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.response_body = response_body


class OPDSNavigationError(OPDSClientError):
    """Error navigating OPDS feed."""

    pass


class OPDSRetryError(OPDSClientError):
    """Error indicating operation should be retried."""

    def __init__(self, message: str, retry_after: int | None = None):
        """Initialize OPDSRetryError.

        Args:
            message: Error message.
            retry_after: Optional seconds to wait before retrying.
        """
        super().__init__(message)
        self.retry_after = retry_after


class SearchError(OPDSClientError):
    """Error during search operation."""

    pass
