"""Tests for OPDS 1.2 models."""

import pytest
from pydantic import ValidationError

from opds_client.opds12.models import (
    AcquisitionLink,
    Entry,
    FacetGroup,
    Feed,
    IndirectAcquisition,
    Link,
    Price,
)


class TestPriceModel:
    """Tests for Price model."""

    def test_create_valid_price(self):
        """Test creating a valid price."""
        price = Price(value="19.99", currencycode="USD")
        assert price.value == "19.99"
        assert price.currencycode == "USD"

    def test_invalid_currency(self):
        """Test invalid currency code."""
        with pytest.raises(ValidationError):
            Price(value="19.99", currencycode="US")


class TestLinkModel:
    """Tests for Link model."""

    def test_basic_link(self):
        """Test basic link creation."""
        link = Link(
            href="https://example.com",
            rel="http://opds-spec.org/acquisition",
            type="application/epub+zip",
        )
        assert link.is_acquisition_link() is True

    def test_non_acquisition_link(self):
        """Test non-acquisition link."""
        link = Link(
            href="https://example.com",
            rel="self",
            type="application/atom+xml",
        )
        assert link.is_acquisition_link() is False


class TestEntryModel:
    """Tests for Entry model."""

    def test_create_valid_entry(self):
        """Test creating a valid entry."""
        entry = Entry(
            id="urn:uuid:test",
            title="Test Entry",
            updated="2010-01-10T10:00:00Z",
            links=[
                Link(
                    href="https://example.com",
                    rel="http://opds-spec.org/acquisition",
                ),
            ],
        )
        assert entry.title == "Test Entry"
        assert entry.is_complete_entry() is True

    def test_entry_requires_acquisition_link(self):
        """Test entry with valid acquisition link."""
        entry = Entry(
            id="urn:uuid:test",
            title="Test Entry",
            updated="2010-01-10T10:00:00Z",
            links=[
                Link(
                    href="https://example.com",
                    rel="http://opds-spec.org/acquisition",
                ),
            ],
        )
        assert entry.is_complete_entry() is True

    def test_link_without_rel(self):
        """Test link without rel attribute (allowed per Atom spec)."""
        link = Link(
            href="https://example.com",
            title="Test Link",
        )
        assert link.href == "https://example.com"
        assert link.title == "Test Link"
        assert link.rel is None

    def test_partial_entry(self):
        """Test partial entry with alternate link."""
        entry = Entry(
            id="urn:uuid:test",
            title="Test Entry",
            updated="2010-01-10T10:00:00Z",
            links=[
                Link(
                    href="https://example.com",
                    rel="http://opds-spec.org/acquisition",
                ),
                Link(
                    href="https://example.com/complete",
                    rel="alternate",
                ),
            ],
        )
        assert entry.is_partial_entry() is True


class TestFeedModel:
    """Tests for Feed model."""

    def test_create_valid_feed(self):
        """Test creating a valid feed."""
        feed = Feed(
            id="urn:uuid:test",
            title="Test Feed",
            updated="2010-01-10T10:00:00Z",
            links=[
                Link(href="https://example.com", rel="self"),
            ],
        )
        assert feed.title == "Test Feed"

    def test_feed_requires_links(self):
        """Test feed requires links."""
        with pytest.raises(ValidationError):
            Feed(
                id="urn:uuid:test",
                title="Test Feed",
                updated="2010-01-10T10:00:00Z",
                links=[],
            )


class TestFacetGroupModel:
    """Tests for FacetGroup model."""

    def test_create_valid_facet_group(self):
        """Test creating a valid facet group."""
        group = FacetGroup(
            title="Categories",
            links=[
                Link(href="/cat1", rel="cat1", title="Category 1"),
                Link(href="/cat2", rel="cat2", title="Category 2"),
            ],
        )
        assert group.title == "Categories"
        assert len(group.links) == 2

    def test_facet_group_requires_links(self):
        """Test facet group requires at least one link."""
        with pytest.raises(ValidationError):
            FacetGroup(
                title="Categories",
                links=[],
            )


class TestAcquisitionLinkModel:
    """Tests for AcquisitionLink model."""

    def test_buy_link_requires_price(self):
        """Test buy link requires price."""
        with pytest.raises(ValidationError):
            AcquisitionLink(
                href="https://example.com",
                rel="http://opds-spec.org/acquisition/buy",
            )

    def test_acquisition_link_with_price(self):
        """Test acquisition link with price."""
        link = AcquisitionLink(
            href="https://example.com",
            rel="http://opds-spec.org/acquisition/buy",
            properties={"price": Price(value="19.99", currencycode="USD")},
        )
        assert link.get_price() is not None


class TestIndirectAcquisitionModel:
    """Tests for IndirectAcquisition model."""

    def test_simple_indirect_acquisition(self):
        """Test simple indirect acquisition."""
        acq = IndirectAcquisition(type="application/epub+zip")
        assert acq.type == "application/epub+zip"

    def test_nested_indirect_acquisition(self):
        """Test nested indirect acquisition."""
        child = IndirectAcquisition(type="application/pdf")
        parent = IndirectAcquisition(
            type="text/html",
            child=[child],
        )
        assert parent.child is not None
        assert len(parent.child) == 1
