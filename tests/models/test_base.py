"""Tests for OPDS base models."""

import pytest
from pydantic import ValidationError

from opds_client.opds2.models import (
    FacetLink,
    ImageLink,
    Link,
    Metadata,
    NavigationLink,
    Price,
)


class TestPriceModel:
    """Tests for Price model."""

    def test_create_valid_price(self):
        """Test creating a valid price."""
        price = Price(currency="USD", value=9.99)
        assert price.currency == "USD"
        assert price.value == 9.99

    def test_invalid_currency(self):
        """Test invalid currency code."""
        with pytest.raises(ValidationError):
            Price(currency="US", value=9.99)

    def test_negative_value(self):
        """Test negative price value."""
        with pytest.raises(ValidationError):
            Price(currency="USD", value=-1.0)


class TestLinkModel:
    """Tests for Link model."""

    def test_basic_link(self):
        """Test basic link creation."""
        link = Link(href="https://example.com")
        assert str(link.href) == "https://example.com"

    def test_link_with_relations(self):
        """Test link with relations."""
        link = Link(
            href="https://example.com",
            rel="self",
            type="application/json",
        )
        assert link.rel == "self"

    def test_link_with_list_relations(self):
        """Test link with list of relations."""
        link = Link(
            href="https://example.com",
            rel=["self", "prev"],
        )
        assert isinstance(link.rel, list)

    def test_templated_link(self):
        """Test templated link."""
        link = Link(
            href="https://example.com/search{?query}",
            templated=True,
        )
        assert link.templated is True
        assert link.fill_template(query="test").startswith("https://example.com/search")

    def test_templated_without_template(self):
        """Test validation error on templated without actual template."""
        with pytest.raises(ValidationError):
            Link(
                href="https://example.com/search",
                templated=True,
            )

    def test_is_navigation_link(self):
        """Test navigation link detection."""
        link = Link(href="https://example.com", rel="navigation")
        assert link.is_navigation_link() is True

    def test_is_search_link(self):
        """Test search link detection."""
        link = Link(
            href="https://example.com/search{?query}", rel="search", templated=True
        )
        assert link.is_search_link() is True


class TestNavigationLinkModel:
    """Tests for NavigationLink model."""

    def test_navigation_link_without_title(self):
        """Test validation requires title."""
        with pytest.raises(ValidationError):
            NavigationLink(
                href="https://example.com",
                rel="navigation",
            )

    def test_navigation_link_valid(self):
        """Test valid navigation link."""
        nav = NavigationLink(
            href="https://example.com",
            title="Test",
            rel="navigation",
        )
        assert nav.title == "Test"


class TestImageLinkModel:
    """Tests for ImageLink model."""

    def test_image_link_with_dimensions(self):
        """Test image link with dimensions."""
        image = ImageLink(
            href="https://example.com/image.jpg",
            type="image/jpeg",
            height=100,
            width=200,
        )
        assert image.height == 100
        assert image.width == 200

    def test_invalid_image_type(self):
        """Test invalid image type."""
        with pytest.raises(ValidationError):
            ImageLink(
                href="https://example.com/image.txt",
                type="text/plain",
            )

    def test_valid_image_types(self):
        """Test valid image types."""
        valid_types = [
            "image/jpeg",
            "image/avif",
            "image/webp",
            "image/jxl",
            "image/png",
            "image/gif",
        ]
        for img_type in valid_types:
            image = ImageLink(
                href="https://example.com/image",
                type=img_type,
            )
            assert image.type == img_type


class TestFacetLinkModel:
    """Tests for FacetLink model."""

    def test_facet_link_with_properties(self):
        """Test facet link with properties."""
        link = FacetLink(
            href="https://example.com/filter",
            title="Filter",
            properties={"numberOfItems": 42},
        )
        assert link.get_number_of_items() == 42

    def test_facet_link_active(self):
        """Test active facet link."""
        link = FacetLink(
            href="https://example.com/current",
            rel="self",
        )
        assert link.is_active() is True

    def test_facet_link_not_active(self):
        """Test non-active facet link."""
        link = FacetLink(
            href="https://example.com/other",
            rel="alternate",
        )
        assert link.is_active() is False


class TestMetadataModel:
    """Tests for Metadata model."""

    def test_basic_metadata(self):
        """Test basic metadata."""
        metadata = Metadata(title="Test Feed")
        assert metadata.title == "Test Feed"

    def test_metadata_with_pagination(self):
        """Test metadata with pagination."""
        metadata = Metadata(
            title="Paginated",
            numberOfItems=100,
            itemsPerPage=20,
            currentPage=3,
        )
        assert metadata.numberOfItems == 100
        assert metadata.itemsPerPage == 20
        assert metadata.currentPage == 3

    def test_metadata_with_language_list(self):
        """Test metadata with language list."""
        metadata = Metadata(
            title="Multilingual",
            language=["en", "fr", "es"],
        )
        assert isinstance(metadata.language, list)
