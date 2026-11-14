"""Tests for OPDS utilities."""


from opds_client.utils import (
    clean_blank_values,
    extract_uri_template_params,
    get_media_type_from_url,
    is_opds_feed_type,
    is_uri_template,
    merge_urls,
    validate_identifier,
)


class TestMergeURLs:
    """Tests for merge_urls function."""

    def test_merge_absolute_url(self):
        """Test merging absolute URL."""
        result = merge_urls("https://example.com/base", "https://other.com/resource")
        assert result == "https://other.com/resource"

    def test_merge_relative_url(self):
        """Test merging relative URL."""
        result = merge_urls("https://example.com/base/", "resource")
        assert result == "https://example.com/base/resource"

    def test_merge_with_dot(self):
        """Test merging URL with dot notation."""
        result = merge_urls("https://example.com/base/path/", "../resource")
        assert result == "https://example.com/base/resource"


class TestURITemplateUtils:
    """Tests for URI template utilities."""

    def test_extract_params(self):
        """Test extracting parameters from template."""
        template = "https://example.com/search{?query,title}"
        params = extract_uri_template_params(template)
        assert "query" in params
        assert "title" in params

    def test_is_uri_template(self):
        """Test detecting URI templates."""
        assert is_uri_template("https://example.com/search{?query}")
        assert not is_uri_template("https://example.com/search")


class TestMediaTypeUtils:
    """Tests for media type utilities."""

    def test_get_media_type_epub(self):
        """Test getting media type for EPUB."""
        media_type = get_media_type_from_url("https://example.com/book.epub")
        assert media_type == "application/epub+zip"

    def test_get_media_type_pdf(self):
        """Test getting media type for PDF."""
        media_type = get_media_type_from_url("https://example.com/book.pdf")
        assert media_type == "application/pdf"

    def test_get_media_type_unknown(self):
        """Test getting media type for unknown extension."""
        media_type = get_media_type_from_url("https://example.com/book.txt")
        assert media_type is None

    def test_is_opds_feed_type(self):
        """Test OPDS feed type detection."""
        assert is_opds_feed_type("application/opds+json") is True
        assert is_opds_feed_type("application/opds-publication+json") is True
        assert is_opds_feed_type("application/json") is False
        assert is_opds_feed_type(None) is False


class TestCleanBlankValues:
    """Tests for clean_blank_values function."""

    def test_clean_none_values(self):
        """Test cleaning None values."""
        data = {
            "title": "Test",
            "description": None,
            "empty_list": [],
        }
        result = clean_blank_values(data)
        assert "title" in result
        assert "description" not in result
        assert "empty_list" not in result

    def test_clean_empty_dict(self):
        """Test cleaning empty dict."""
        data = {
            "title": "Test",
            "empty": {},
            "nested": {"key": None},
        }
        result = clean_blank_values(data)
        assert "title" in result
        assert "empty" not in result
        assert "nested" not in result

    def test_clean_empty_string(self):
        """Test cleaning empty strings."""
        data = {
            "title": "Test",
            "description": "",
        }
        result = clean_blank_values(data)
        assert "title" in result
        assert "description" not in result


class TestValidateIdentifier:
    """Tests for validate_identifier function."""

    def test_valid_isbn(self):
        """Test valid ISBN."""
        assert validate_identifier("urn:isbn:9780000000000") is True

    def test_valid_doi(self):
        """Test valid DOI."""
        assert validate_identifier("doi:10.1234/test") is True

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        assert validate_identifier("http://example.com/identifier") is True

    def test_invalid_identifier(self):
        """Test invalid identifier."""
        assert validate_identifier("invalid") is False
        assert validate_identifier("") is False
