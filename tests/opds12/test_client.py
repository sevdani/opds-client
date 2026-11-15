"""Tests for OPDS 1.2 client."""

import os
from unittest.mock import Mock, patch

import pytest
import requests

from opds_client.opds12.client import OPDS12Client
from opds_client.opds12.exceptions import OPDSHTTPError


class TestOPDS12Client:
    """Tests for OPDS 1.2 client."""

    @patch("requests.Session.get")
    def test_fetch_feed_success(self, mock_get):
        """Test fetching a feed successfully."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "root.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client()
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.title == "OPDS Catalog Root Example"
        assert feed.id == "urn:uuid:2853dacf-ed79-42f5-8e8a-a7bb3d1ae6a2"
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_fetch_feed_http_error(self, mock_get):
        """Test handling HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        client = OPDS12Client()

        with pytest.raises(OPDSHTTPError) as exc_info:
            client.fetch_feed("https://example.com/opds")

        assert exc_info.value.status_code == 404

    @patch("requests.Session.get")
    def test_fetch_entry(self, mock_get):
        """Test fetching an entry."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "acquisition.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client()
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.is_acquisition_feed() is True
        assert feed.has_entries() is True
        assert len(feed.entries) == 2

    @patch("requests.Session.get")
    def test_navigation_links(self, mock_get):
        """Test navigation link parsing."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "root.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client()
        feed = client.fetch_feed("https://example.com/opds")

        # Check navigation links
        start_link = feed.get_start_link()
        assert start_link is not None
        assert start_link.rel == "start"

    @patch("requests.Session.get")
    def test_pagination_links(self, mock_get):
        """Test pagination link parsing."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "acquisition.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client()
        feed = client.fetch_feed("https://example.com/opds")

        # Check acquisition feed type
        assert feed.is_acquisition_feed() is True
        assert feed.is_navigation_feed() is False

    def test_context_manager(self):
        """Test client as context manager."""
        with OPDS12Client() as client:
            assert client is not None

    @patch("requests.Session.get")
    def test_basic_auth(self, mock_get):
        """Test HTTP Basic Auth."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "root.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client(username="user", password="pass")
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.title == "OPDS Catalog Root Example"
        assert client.session.auth is not None

    @patch("requests.Session.get")
    def test_custom_auth(self, mock_get):
        """Test custom auth object."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "root.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        from requests.auth import HTTPBasicAuth

        custom_auth = HTTPBasicAuth("custom", "auth")
        client = OPDS12Client(auth=custom_auth)
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.title == "OPDS Catalog Root Example"
        assert client.session.auth is custom_auth

    @patch("requests.Session.get")
    def test_origin_with_relative_url(self, mock_get):
        """Test origin parameter with relative URL."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "root.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client(origin="https://api.example.com")
        client.fetch_feed("/catalog.xml")

        called_url = mock_get.call_args[0][0]
        assert called_url == "https://api.example.com/catalog.xml"

    @patch("requests.Session.get")
    def test_origin_with_absolute_url(self, mock_get):
        """Test origin parameter with absolute URL (should not merge)."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "root.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client(origin="https://api.example.com")
        client.fetch_feed("https://other.com/catalog.xml")

        called_url = mock_get.call_args[0][0]
        assert called_url == "https://other.com/catalog.xml"

    @patch("requests.Session.get")
    def test_origin_without_parameter(self, mock_get):
        """Test client without origin parameter (should use URLs as-is)."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(fixtures_dir, "root.xml")) as f:
            feed_xml = f.read()

        mock_response = Mock()
        mock_response.text = feed_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDS12Client()
        client.fetch_feed("/catalog.xml")

        called_url = mock_get.call_args[0][0]
        assert called_url == "/catalog.xml"
