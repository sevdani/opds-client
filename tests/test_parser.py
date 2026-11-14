"""Tests for OPDS parser."""

import json

import pytest

from opds_client.exceptions import OPDSParseError, OPDSValidationError
from opds_client.parser import OPDSParser, URITemplateResolver


class TestOPDSParser:
    """Tests for OPDS parser."""

    def test_parse_valid_json_feed(self):
        """Test parsing valid OPDS feed JSON."""
        parser = OPDSParser()

        feed_json = json.dumps(
            {
                "metadata": {"title": "Test Feed"},
                "links": [{"rel": "self", "href": "https://example.com"}],
                "navigation": [{"href": "/nav", "title": "Navigation"}],
            }
        )

        feed = parser.parse(feed_json)

        assert feed.metadata.title == "Test Feed"
        assert feed.has_navigation() is True

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        parser = OPDSParser()

        with pytest.raises(OPDSParseError):
            parser.parse("not valid json")

    def test_parse_publication(self):
        """Test parsing publication."""
        parser = OPDSParser()

        pub_json = json.dumps(
            {
                "metadata": {
                    "title": "Test Book",
                    "identifier": "urn:isbn:1234567890",
                },
                "links": [
                    {"rel": "self", "href": "https://example.com"},
                    {"rel": "download", "href": "https://example.com/download.epub"},
                ],
            }
        )

        pub = parser.parse_publication(pub_json)

        assert pub.metadata.title == "Test Book"
        assert len(pub.get_acquisition_links()) == 1

    def test_strict_mode_validation_error(self):
        """Test strict mode raises validation error."""
        parser = OPDSParser(strict=True)

        invalid_feed = json.dumps(
            {
                "metadata": {},  # Missing required title
                "links": [{"rel": "self", "href": "https://example.com"}],
            }
        )

        with pytest.raises(OPDSValidationError):
            parser.parse(invalid_feed)

    def test_non_strict_mode_warnings(self):
        """Test non-strict mode collects warnings."""
        parser = OPDSParser(strict=False)

        # Feed with invalid navigation (missing title) but valid publications
        invalid_feed = json.dumps(
            {
                "metadata": {"title": "Test"},
                "links": [{"rel": "self", "href": "https://example.com"}],
                "navigation": [{"href": "/nav"}],  # Missing title - invalid
                "publications": [
                    {
                        "metadata": {"title": "Book", "identifier": "urn:isbn:123"},
                        "links": [
                            {"rel": "self", "href": "https://example.com"},
                            {
                                "rel": "download",
                                "href": "https://example.com/download.epub",
                            },
                        ],
                    }
                ],
            }
        )

        feed = parser.parse(invalid_feed)

        # Should have warnings about invalid navigation
        assert len(parser.warnings) > 0
        # But should still parse successfully
        assert feed.metadata.title == "Test"
        assert feed.has_publications() is True

    def test_parse_feed_with_images(self):
        """Test parsing feed with images."""
        parser = OPDSParser()

        feed_json = json.dumps(
            {
                "metadata": {"title": "Test"},
                "links": [{"rel": "self", "href": "https://example.com"}],
                "publications": [
                    {
                        "metadata": {
                            "title": "Book",
                            "identifier": "urn:isbn:123",
                        },
                        "links": [
                            {"rel": "self", "href": "https://example.com"},
                            {
                                "rel": "download",
                                "href": "https://example.com/download.epub",
                            },
                        ],
                        "images": [
                            {
                                "href": "https://example.com/cover.jpg",
                                "type": "image/jpeg",
                                "height": 100,
                                "width": 200,
                            }
                        ],
                    }
                ],
            }
        )

        feed = parser.parse(feed_json)
        assert feed.publications is not None
        assert len(feed.publications) == 1
        assert feed.publications[0].images is not None
        assert len(feed.publications[0].images) == 1

    def test_parse_facets(self):
        """Test parsing facets."""
        parser = OPDSParser()

        feed_json = json.dumps(
            {
                "metadata": {"title": "Test"},
                "links": [{"rel": "self", "href": "https://example.com"}],
                "facets": [
                    {
                        "metadata": {"title": "Filter"},
                        "links": [
                            {"href": "/f1", "title": "F1"},
                            {"href": "/f2", "title": "F2"},
                        ],
                    }
                ],
            }
        )

        feed = parser.parse(feed_json)
        assert feed.has_facets() is True
        assert len(feed.facets) == 1

    def test_parse_groups(self):
        """Test parsing groups."""
        parser = OPDSParser()

        feed_json = json.dumps(
            {
                "metadata": {"title": "Test"},
                "links": [{"rel": "self", "href": "https://example.com"}],
                "groups": [
                    {
                        "metadata": {"title": "Group"},
                        "navigation": [{"href": "/nav", "title": "Nav"}],
                    }
                ],
            }
        )

        feed = parser.parse(feed_json)
        assert feed.has_groups() is True
        assert len(feed.groups) == 1


class TestURITemplateResolver:
    """Tests for URI template resolver."""

    def test_resolve_basic_template(self):
        """Test resolving basic URI template."""
        template = "https://example.com/search{?query}"
        result = URITemplateResolver.fill_template(template, query="test")
        assert "search" in result

    def test_resolve_multiple_params(self):
        """Test resolving template with multiple parameters."""
        template = "https://example.com/search{?query,title}"
        result = URITemplateResolver.fill_template(
            template,
            query="test",
            title="My Book",
        )
        assert "search" in result

    def test_resolve_without_substitution(self):
        """Test resolving without providing params."""
        template = "https://example.com/search{?query}"
        result = URITemplateResolver.fill_template(template)
        assert "search" in result

    def test_extract_params(self):
        """Test extracting parameter names."""
        template = "https://example.com/search{?query,title}"
        params = URITemplateResolver._extract_params(template)
        assert "query" in params
        assert "title" in params
