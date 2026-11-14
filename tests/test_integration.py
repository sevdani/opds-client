"""Tests for OPDS client integration."""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from opds_client.client import OPDSClient
from opds_client.exceptions import OPDSHTTPError, OPDSNavigationError, SearchError
from opds_client.parser import OPDSParser


class TestOPDSClientIntegration:
    """Integration tests for OPDS client."""

    @patch("requests.Session.get")
    def test_fetch_feed(self, mock_get):
        """Test fetching an OPDS feed."""

        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDSClient()
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.metadata.title == "Test OPDS Feed"
        assert feed.has_navigation() is True
        assert feed.has_publications() is True
        assert feed.has_facets() is True

    @patch("requests.Session.get")
    def test_fetch_publication(self, mock_get):
        """Test fetching an OPDS publication."""
        with open("tests/fixtures/publication.json") as f:
            pub_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(pub_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDSClient()
        pub = client.fetch_publication("https://example.com/publication")

        assert pub.metadata.title == "Test Publication"
        assert pub.get_self_link() is not None

    @patch("requests.Session.get")
    def test_follow_navigation_link(self, mock_get):
        """Test following a navigation link."""
        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(feed_data)

        client = OPDSClient()
        nav_link = feed.navigation[0]
        result = client.follow_link(nav_link)

        assert result.metadata.title == "Test OPDS Feed"

    @patch("requests.Session.get")
    def test_search_catalog(self, mock_get):
        """Test searching the catalog."""
        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(feed_data)

        client = OPDSClient()
        results = client.search(feed, "test query")

        assert results.metadata.title == "Test OPDS Feed"

    @patch("requests.Session.get")
    def test_navigation_by_title(self, mock_get):
        """Test navigating by title."""
        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(feed_data)

        client = OPDSClient()
        result = client.follow_navigation(feed, "New Publications")

        assert result.metadata.title == "Test OPDS Feed"

    def test_search_not_supported(self):
        """Test search when not supported by catalog."""
        parser = OPDSParser()

        feed_data = {
            "metadata": {"title": "Feed without search"},
            "links": [{"rel": "self", "href": "https://example.com"}],
            "navigation": [
                {"href": "https://example.com/nav", "title": "Navigation"}
            ],
        }
        feed = parser.parse_dict(feed_data)

        client = OPDSClient()

        with pytest.raises(SearchError):
            client.search(feed, "test")

    @patch("requests.Session.get")
    def test_pagination_next_link(self, mock_get):
        """Test pagination with next link."""
        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(feed_data)

        client = OPDSClient()
        next_feed = client.get_next_page(feed)

        assert next_feed is not None
        assert next_feed.metadata.title == "Test OPDS Feed"

    @patch("requests.Session.get")
    def test_pagination_previous_link(self, mock_get):
        """Test pagination with previous link."""
        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(feed_data)

        client = OPDSClient()
        prev_feed = client.get_previous_page(feed)

        assert prev_feed is not None
        assert prev_feed.metadata.title == "Test OPDS Feed"

    @patch("requests.Session.get")
    def test_facet_navigation(self, mock_get):
        """Test navigating facets."""
        with open("tests/fixtures/facets.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(feed_data)

        OPDSClient()

        facet = feed.get_facets_by_title("Sort By")
        assert facet is not None

        link = facet.get_facet_by_title("Date")
        assert link is not None

    @patch("requests.Session.get")
    def test_groups_navigation(self, mock_get):
        """Test navigating groups."""
        with open("tests/fixtures/groups.json") as f:
            feed_data = json.load(f)

        mock_response = Mock()
        mock_response.text = json.dumps(feed_data)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(feed_data)

        assert feed.has_groups() is True

        featured_group = None
        for group in feed.groups:
            if group.metadata.title == "Featured Books":
                featured_group = group
                break

        assert featured_group is not None
        assert featured_group.has_publications() is True

    def test_http_error_handling(self):
        """Test HTTP error handling."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_get.return_value = mock_response

            client = OPDSClient()

            with pytest.raises(OPDSHTTPError) as exc_info:
                client.fetch_feed("https://example.com/opds")

            assert exc_info.value.status_code == 404

    def test_navigation_error(self):
        """Test navigation error handling."""
        parser = OPDSParser()

        feed_data = {
            "metadata": {"title": "Feed without navigation"},
            "links": [{"rel": "self", "href": "https://example.com"}],
            "navigation": [
                {"href": "https://example.com/nav", "title": "Other"}
            ],
        }
        feed = parser.parse_dict(feed_data)

        client = OPDSClient()

        with pytest.raises(OPDSNavigationError):
            client.follow_navigation(feed, "Non-existent")

    def test_context_manager(self):
        """Test client as context manager."""
        with OPDSClient() as client:
            assert client is not None

    def test_custom_session(self):
        """Test using custom session."""
        session = requests.Session()
        session.headers.update({"X-Custom": "value"})

        client = OPDSClient(session=session)
        assert client.session == session

    def test_no_retries(self):
        """Test client with no retries."""
        client = OPDSClient(max_retries=0)
        assert client is not None
