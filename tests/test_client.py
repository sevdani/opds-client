"""Tests for OPDS 2.0 client."""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from opds_client.client import OPDSClient
from opds_client.exceptions import (
    OPDSHTTPError,
    OPDSNavigationError,
    SearchError,
)
from opds_client.models import (
    AcquisitionLink,
    Link,
    Metadata,
    NavigationLink,
    OPDSFeed,
    OPDSPublication,
    Publication,
)
from opds_client.parser import OPDSParser, URITemplateResolver


class TestURITemplateResolver:
    """Tests for URI template resolution."""

    def test_resolve_simple_template(self):
        """Test resolving a simple URI template."""
        template = "https://example.com/search{?query}"
        result = URITemplateResolver.fill_template(template, query="test")
        assert "search" in result

    def test_resolve_multiple_params(self):
        """Test resolving template with multiple parameters."""
        template = "https://example.com/search{?query,title,author}"
        result = URITemplateResolver.fill_template(
            template,
            query="test",
            title="My Book",
            author="John Doe",
        )
        assert "search" in result

    def test_resolve_without_params(self):
        """Test resolving template without providing params."""
        template = "https://example.com/search{?query}"
        result = URITemplateResolver.fill_template(template)
        assert "search" in result

    def test_extract_params(self):
        """Test extracting parameter names from template."""
        template = "https://example.com/search{?query,title}"
        params = URITemplateResolver._extract_params(template)
        assert "query" in params
        assert "title" in params

    def test_is_uri_template(self):
        """Test detecting URI templates."""
        from opds_client.utils import is_uri_template
        assert is_uri_template("https://example.com/search{?query}")
        assert not is_uri_template("https://example.com/search")


class TestLinkModel:
    """Tests for Link model."""

    def test_create_basic_link(self):
        """Test creating a basic link."""
        link = Link(href="https://example.com")
        assert link.href == "https://example.com"
        assert link.rel is None
        assert link.templated is False

    def test_create_templated_link(self):
        """Test creating a templated link."""
        link = Link(
            href="https://example.com/search{?query}",
            rel="search",
            templated=True,
        )
        assert link.templated is True
        assert link.rel == "search"

    def test_fill_template(self):
        """Test filling URI template."""
        link = Link(
            href="https://example.com/search{?query}",
            templated=True,
        )
        result = link.fill_template(query="test")
        assert "search" in result

    def test_navigation_link_requires_title(self):
        """Test that navigation links must have a title."""
        with pytest.raises(Exception):
            NavigationLink(
                href="https://example.com",
                rel="navigation",
            )

    def test_navigation_link_valid(self):
        """Test valid navigation link."""
        nav_link = NavigationLink(
            href="https://example.com",
            title="Test",
            rel="navigation",
        )
        assert nav_link.title == "Test"


class TestMetadataModel:
    """Tests for Metadata model."""

    def test_create_basic_metadata(self):
        """Test creating basic metadata."""
        metadata = Metadata(title="Test Feed")
        assert metadata.title == "Test Feed"

    def test_metadata_with_pagination(self):
        """Test metadata with pagination fields."""
        metadata = Metadata(
            title="Paginated Feed",
            numberOfItems=100,
            itemsPerPage=20,
            currentPage=1,
        )
        assert metadata.numberOfItems == 100
        assert metadata.itemsPerPage == 20
        assert metadata.currentPage == 1


class TestAcquisitionLinkModel:
    """Tests for Acquisition Link model."""

    def test_create_download_link(self):
        """Test creating a download link."""
        link = AcquisitionLink(
            href="https://example.com/download",
            rel="download",
            type="application/epub+zip",
        )
        assert link.rel == "download"
        assert link.is_open_access() is True

    def test_create_buy_link(self):
        """Test creating a buy link with price."""
        link = AcquisitionLink(
            href="https://example.com/buy",
            rel="buy",
            type="application/epub+zip",
            properties={
                "price": {"currency": "USD", "value": 9.99}
            },
        )
        assert link.rel == "buy"
        assert link.is_open_access() is False
        assert link.get_price() is not None
        assert link.get_price().currency == "USD"
        assert link.get_price().value == 9.99


class TestPublicationModel:
    """Tests for Publication model."""

    def test_create_basic_publication(self):
        """Test creating a basic publication."""
        pub = Publication(
            metadata=Metadata(title="Test Book"),
            links=[Link(href="https://example.com", rel="self")],
        )
        assert pub.metadata.title == "Test Book"
        assert len(pub.links) == 1

    def test_opds_publication_requires_acquisition(self):
        """Test that OPDS publication requires acquisition link."""
        with pytest.raises(Exception):
            OPDSPublication(
                metadata=Metadata(title="Test Book"),
                links=[Link(href="https://example.com", rel="self")],
            )

    def test_opds_publication_valid(self):
        """Test valid OPDS publication."""
        pub = OPDSPublication(
            metadata=Metadata(title="Test Book"),
            links=[
                Link(href="https://example.com", rel="self"),
                Link(href="https://example.com/download", rel="download"),
            ],
        )
        assert pub.get_self_link() is not None
        assert len(pub.get_acquisition_links()) == 1


class TestFeedParser:
    """Tests for OPDS feed parser."""

    def test_parse_valid_feed(self):
        """Test parsing a valid OPDS feed."""
        parser = OPDSParser()

        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        feed = parser.parse_dict(feed_data)

        assert isinstance(feed, OPDSFeed)
        assert feed.metadata.title == "Test OPDS Feed"
        assert feed.has_navigation() is True
        assert feed.has_publications() is True
        assert feed.has_facets() is True

    def test_parse_publication(self):
        """Test parsing a publication."""
        parser = OPDSParser()

        with open("tests/fixtures/publication.json") as f:
            pub_data = json.load(f)

        pub = parser.parse_publication_dict(pub_data)

        assert isinstance(pub, OPDSPublication)
        assert pub.metadata.title == "Test Publication"
        assert pub.get_self_link() is not None

    def test_parse_facets(self):
        """Test parsing facets."""
        parser = OPDSParser()

        with open("tests/fixtures/facets.json") as f:
            feed_data = json.load(f)

        feed = parser.parse_dict(feed_data)

        assert feed.has_facets() is True
        assert len(feed.facets) == 3

        sort_facet = feed.get_facets_by_title("Sort By")
        assert sort_facet is not None
        assert len(sort_facet.links) == 3

        active = sort_facet.get_active_facet()
        assert active is not None
        assert active.title == "Date"

    def test_parse_groups(self):
        """Test parsing groups."""
        parser = OPDSParser()

        with open("tests/fixtures/groups.json") as f:
            feed_data = json.load(f)

        feed = parser.parse_dict(feed_data)

        assert feed.has_groups() is True
        assert len(feed.groups) == 3

        featured_group = None
        for group in feed.groups:
            if group.metadata.title == "Featured Books":
                featured_group = group
                break

        assert featured_group is not None
        assert featured_group.has_publications() is True


class TestFeedMethods:
    """Tests for OPDS feed methods."""

    def test_get_link_by_rel(self):
        """Test getting link by relation."""
        parser = OPDSParser()

        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        feed = parser.parse_dict(feed_data)

        search_link = feed.get_link_by_rel("search")
        assert search_link is not None
        assert search_link.templated is True

    def test_pagination_links(self):
        """Test pagination link methods."""
        parser = OPDSParser()

        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        feed = parser.parse_dict(feed_data)

        assert feed.get_next_link() is not None
        assert feed.get_previous_link() is not None
        assert feed.get_first_link() is not None
        assert feed.get_last_link() is not None

    def test_is_searchable(self):
        """Test checking if feed is searchable."""
        parser = OPDSParser()

        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        feed = parser.parse_dict(feed_data)

        assert feed.is_searchable() is True

    def test_get_facet_by_title(self):
        """Test getting facet by title."""
        parser = OPDSParser()

        with open("tests/fixtures/feed.json") as f:
            feed_data = json.load(f)

        feed = parser.parse_dict(feed_data)

        lang_facet = feed.get_facets_by_title("Language")
        assert lang_facet is not None
        assert lang_facet.metadata.title == "Language"

    def test_get_publication_image(self):
        """Test getting publication image by type."""
        parser = OPDSParser()

        with open("tests/fixtures/publication.json") as f:
            pub_data = json.load(f)

        pub = parser.parse_publication_dict(pub_data)

        jpeg_image = pub.get_image_by_type("image/jpeg")
        assert jpeg_image is not None
        assert jpeg_image.height == 1600


class TestOPDSClient:
    """Tests for OPDS client."""

    @patch("requests.Session.get")
    def test_fetch_feed_success(self, mock_get):
        """Test fetching a feed successfully."""
        with open("tests/fixtures/feed.json") as f:
            feed_json = f.read()

        mock_response = Mock()
        mock_response.text = feed_json
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDSClient()
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.metadata.title == "Test OPDS Feed"
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

        client = OPDSClient()

        with pytest.raises(OPDSHTTPError) as exc_info:
            client.fetch_feed("https://example.com/opds")

        assert exc_info.value.status_code == 404

    @patch("requests.Session.get")
    def test_follow_link(self, mock_get):
        """Test following a link."""
        with open("tests/fixtures/feed.json") as f:
            feed_json = f.read()

        mock_response = Mock()
        mock_response.text = feed_json
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(json.loads(feed_json))

        nav_link = feed.navigation[0] if feed.navigation else None
        assert nav_link is not None

        client = OPDSClient()
        result = client.follow_link(nav_link)

        assert result.metadata.title == "Test OPDS Feed"

    @patch("requests.Session.get")
    def test_search(self, mock_get):
        """Test search functionality."""
        with open("tests/fixtures/feed.json") as f:
            feed_json = f.read()

        mock_response = Mock()
        mock_response.text = feed_json
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(json.loads(feed_json))

        client = OPDSClient()
        results = client.search(feed, "test query")

        assert results.metadata.title == "Test OPDS Feed"

    def test_search_not_supported(self):
        """Test search when not supported."""
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

        with pytest.raises(SearchError) as exc_info:
            client.search(feed, "test")

        assert "Search is not supported" in str(exc_info.value)

    @patch("requests.Session.get")
    def test_navigation_by_title(self, mock_get):
        """Test navigating by title."""
        with open("tests/fixtures/feed.json") as f:
            feed_json = f.read()

        mock_response = Mock()
        mock_response.text = feed_json
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        parser = OPDSParser()
        feed = parser.parse_dict(json.loads(feed_json))

        client = OPDSClient()
        result = client.follow_navigation(feed, "New Publications")

        assert result.metadata.title == "Test OPDS Feed"

    def test_navigation_not_found(self):
        """Test navigation when link not found."""
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

        with pytest.raises(OPDSNavigationError) as exc_info:
            client.follow_navigation(feed, "Non-existent")

        assert "not found" in str(exc_info.value)

    def test_context_manager(self):
        """Test client as context manager."""
        with OPDSClient() as client:
            assert client is not None

    @patch("requests.Session.get")
    def test_basic_auth(self, mock_get):
        """Test HTTP Basic Auth."""
        with open("tests/fixtures/feed.json") as f:
            feed_json = f.read()

        mock_response = Mock()
        mock_response.text = feed_json
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OPDSClient(username="user", password="pass")
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.metadata.title == "Test OPDS Feed"
        assert mock_get.call_args.kwargs.get("auth") is None
        assert client.session.auth is not None

    @patch("requests.Session.get")
    def test_custom_auth(self, mock_get):
        """Test custom auth object."""
        with open("tests/fixtures/feed.json") as f:
            feed_json = f.read()

        mock_response = Mock()
        mock_response.text = feed_json
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        from requests.auth import HTTPBasicAuth

        custom_auth = HTTPBasicAuth("custom", "auth")
        client = OPDSClient(auth=custom_auth)
        feed = client.fetch_feed("https://example.com/opds")

        assert feed.metadata.title == "Test OPDS Feed"
        assert client.session.auth is custom_auth

    def test_origin_with_relative_url(self):
        """Test origin parameter with relative URL."""
        from opds_client.parser import OPDSParser
        import json

        parser = OPDSParser()
        feed_data = {
            "metadata": {"title": "Test"},
            "links": [{"rel": "self", "href": "/opds"}],
            "navigation": [{"href": "/nav", "title": "Nav", "type": "application/opds+json"}],
        }
        feed = parser.parse_dict(feed_data)

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.text = json.dumps(feed_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            client = OPDSClient(origin="https://example.com")
            result = client.fetch_feed("/catalog")

            called_url = mock_get.call_args[0][0]
            assert called_url == "https://example.com/catalog"

    def test_origin_with_absolute_url(self):
        """Test origin parameter with absolute URL (should not merge)."""
        from opds_client.parser import OPDSParser
        import json

        parser = OPDSParser()
        feed_data = {
            "metadata": {"title": "Test"},
            "links": [{"rel": "self", "href": "/opds"}],
            "navigation": [{"href": "/nav", "title": "Nav", "type": "application/opds+json"}],
        }
        feed = parser.parse_dict(feed_data)

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.text = json.dumps(feed_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            client = OPDSClient(origin="https://example.com")
            result = client.fetch_feed("https://other.com/catalog")

            called_url = mock_get.call_args[0][0]
            assert called_url == "https://other.com/catalog"

    def test_origin_without_parameter(self):
        """Test client without origin parameter (should use URLs as-is)."""
        from opds_client.parser import OPDSParser
        import json

        parser = OPDSParser()
        feed_data = {
            "metadata": {"title": "Test"},
            "links": [{"rel": "self", "href": "/opds"}],
            "navigation": [{"href": "/nav", "title": "Nav", "type": "application/opds+json"}],
        }
        feed = parser.parse_dict(feed_data)

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.text = json.dumps(feed_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            client = OPDSClient()
            result = client.fetch_feed("/catalog")

            called_url = mock_get.call_args[0][0]
            assert called_url == "/catalog"
