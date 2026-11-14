"""Tests for OPDS feed models."""

import pytest
from pydantic import ValidationError

from opds_client.models import (
    Facet,
    FacetLink,
    Group,
    Link,
    Metadata,
    NavigationLink,
    OPDSFeed,
    OPDSPublication,
)


class TestFeedModel:
    """Tests for OPDSFeed model."""

    def test_feed_without_metadata(self):
        """Test feed requires metadata."""
        with pytest.raises(ValidationError):
            OPDSFeed(
                links=[Link(href="https://example.com", rel="self")],
            )

    def test_feed_without_title(self):
        """Test feed requires title."""
        with pytest.raises(ValidationError):
            OPDSFeed(
                metadata=Metadata(title=""),
                links=[Link(href="https://example.com", rel="self")],
            )

    def test_feed_without_self_link(self):
        """Test feed requires self link."""
        with pytest.raises(ValidationError):
            OPDSFeed(
                metadata=Metadata(title="Test"),
                links=[Link(href="https://example.com", rel="alternate")],
            )

    def test_feed_with_navigation(self):
        """Test feed with navigation collection."""
        feed = OPDSFeed(
            metadata=Metadata(title="Test"),
            links=[Link(href="https://example.com", rel="self")],
            navigation=[
                NavigationLink(
                    href="https://example.com/nav",
                    title="Navigation",
                ),
            ],
        )
        assert feed.has_navigation() is True

    def test_feed_with_publications(self):
        """Test feed with publications collection."""
        feed = OPDSFeed(
            metadata=Metadata(title="Test"),
            links=[Link(href="https://example.com", rel="self")],
            publications=[
                OPDSPublication(
                    metadata=Metadata(title="Book"),
                    links=[
                        Link(href="https://example.com", rel="self"),
                        Link(href="https://example.com/download", rel="download"),
                    ],
                ),
            ],
        )
        assert feed.has_publications() is True

    def test_feed_with_facets(self):
        """Test feed with facets collection."""
        feed = OPDSFeed(
            metadata=Metadata(title="Test"),
            links=[Link(href="https://example.com", rel="self")],
            facets=[
                Facet(
                    metadata=Metadata(title="Filter"),
                    links=[
                        FacetLink(href="https://example.com/f1", title="F1"),
                        FacetLink(href="https://example.com/f2", title="F2"),
                    ],
                ),
            ],
        )
        assert feed.has_facets() is True

    def test_feed_with_groups(self):
        """Test feed with groups collection."""
        feed = OPDSFeed(
            metadata=Metadata(title="Test"),
            links=[Link(href="https://example.com", rel="self")],
            groups=[
                Group(
                    metadata=Metadata(title="Group"),
                    navigation=[
                        NavigationLink(
                            href="https://example.com/nav",
                            title="Nav",
                        ),
                    ],
                ),
            ],
        )
        assert feed.has_groups() is True

    def test_feed_without_any_collection(self):
        """Test feed requires at least one collection."""
        with pytest.raises(ValidationError):
            OPDSFeed(
                metadata=Metadata(title="Test"),
                links=[Link(href="https://example.com", rel="self")],
            )


class TestFacetModel:
    """Tests for Facet model."""

    def test_facet_with_one_link(self):
        """Test facet is valid with a single link (per OPDS 2.0 schema)."""
        facet = Facet(
            metadata=Metadata(title="Filter"),
            links=[FacetLink(href="https://example.com/f1", title="F1")],
        )
        assert len(facet.links) == 1

    def test_facet_with_two_links(self):
        """Test valid facet with 2 links."""
        facet = Facet(
            metadata=Metadata(title="Filter"),
            links=[
                FacetLink(href="https://example.com/f1", title="F1"),
                FacetLink(href="https://example.com/f2", title="F2"),
            ],
        )
        assert len(facet.links) == 2

    def test_get_facet_by_title(self):
        """Test getting facet link by title."""
        facet = Facet(
            metadata=Metadata(title="Filter"),
            links=[
                FacetLink(href="https://example.com/f1", title="First"),
                FacetLink(href="https://example.com/f2", title="Second"),
            ],
        )
        link = facet.get_facet_by_title("Second")
        assert link is not None
        assert link.title == "Second"


class TestGroupModel:
    """Tests for Group model."""

    def test_group_without_navigation_or_publications(self):
        """
        Test group is valid without navigation or publications (per OPDS 2.0 schema).
        """
        group = Group(
            metadata=Metadata(title="Group"),
        )
        assert group.metadata.title == "Group"

    def test_group_with_navigation(self):
        """Test valid group with navigation."""
        group = Group(
            metadata=Metadata(title="Group"),
            navigation=[
                NavigationLink(
                    href="https://example.com/nav",
                    title="Navigation",
                ),
            ],
        )
        assert group.has_navigation() is True

    def test_group_with_publications(self):
        """Test valid group with publications."""
        group = Group(
            metadata=Metadata(title="Group"),
            publications=[
                OPDSPublication(
                    metadata=Metadata(title="Book"),
                    links=[
                        Link(href="https://example.com", rel="self"),
                        Link(href="https://example.com/download", rel="download"),
                    ],
                ),
            ],
        )
        assert group.has_publications() is True
