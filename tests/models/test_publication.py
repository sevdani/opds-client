"""Tests for OPDS publication models."""

import pytest
from pydantic import ValidationError

from opds_client.opds2.models import (
    AcquisitionLink,
    BelongsTo,
    Contributor,
    ImageLink,
    Link,
    Metadata,
    OPDSPublication,
    Publication,
    Series,
)


class TestAcquisitionLinkModel:
    """Tests for AcquisitionLink model."""

    def test_download_link(self):
        """Test download link."""
        link = AcquisitionLink(
            href="https://example.com/download",
            rel="download",
        )
        assert link.is_open_access() is True

    def test_buy_link_with_price(self):
        """Test buy link with price."""
        link = AcquisitionLink(
            href="https://example.com/buy",
            rel="buy",
            properties={"price": {"currency": "EUR", "value": 19.99}},
        )
        assert link.get_price() is not None
        assert link.get_price().currency == "EUR"
        assert link.get_price().value == 19.99

    def test_indirect_acquisition(self):
        """Test indirect acquisition."""
        link = AcquisitionLink(
            href="https://example.com/buy",
            rel="buy",
            properties={
                "price": {"currency": "USD", "value": 9.99},
                "indirectAcquisition": [{"type": "application/epub+zip"}],
            },
        )
        indirect = link.get_indirect_acquisitions()
        assert len(indirect) == 1
        assert indirect[0].type == "application/epub+zip"

    def test_invalid_acquisition_rel(self):
        """Test invalid acquisition relation."""
        with pytest.raises(ValidationError):
            AcquisitionLink(
                href="https://example.com",
                rel="invalid_relation",
            )


class TestPublicationModel:
    """Tests for Publication model."""

    def test_basic_publication(self):
        """Test basic publication."""
        pub = Publication(
            metadata=Metadata(title="Test Book"),
            links=[Link(href="https://example.com", rel="self")],
        )
        assert pub.metadata.title == "Test Book"
        assert len(pub.links) == 1

    def test_publication_with_contributor(self):
        """Test publication with contributor."""
        pub = Publication(
            metadata=Metadata(
                title="Test Book",
            ),
            links=[Link(href="https://example.com", rel="self")],
        )
        assert pub.metadata.title == "Test Book"

    def test_publication_with_images(self):
        """Test publication with images."""
        pub = Publication(
            metadata=Metadata(title="Test Book"),
            links=[Link(href="https://example.com", rel="self")],
            images=[
                ImageLink(
                    href="https://example.com/image.jpg",
                    type="image/jpeg",
                    height=100,
                    width=200,
                )
            ],
        )
        assert len(pub.images) == 1

    def test_get_self_link(self):
        """Test getting self link."""
        pub = Publication(
            metadata=Metadata(title="Test Book"),
            links=[
                Link(href="https://example.com/self", rel="self"),
                Link(href="https://example.com/other", rel="alternate"),
            ],
        )
        self_link = pub.get_self_link()
        assert self_link is not None
        assert str(self_link.href) == "https://example.com/self"

    def test_get_image_by_type(self):
        """Test getting image by type."""
        pub = Publication(
            metadata=Metadata(title="Test Book"),
            links=[Link(href="https://example.com", rel="self")],
            images=[
                ImageLink(
                    href="https://example.com/cover.jpg",
                    type="image/jpeg",
                ),
                ImageLink(
                    href="https://example.com/cover.png",
                    type="image/png",
                ),
            ],
        )
        jpeg = pub.get_image_by_type("image/jpeg")
        assert jpeg is not None
        assert jpeg.href == "https://example.com/cover.jpg"


class TestOPDSPublicationModel:
    """Tests for OPDSPublication model."""

    def test_opds_publication_without_acquisition(self):
        """Test OPDS publication requires acquisition."""
        with pytest.raises(ValidationError):
            OPDSPublication(
                metadata=Metadata(title="Test Book"),
                links=[
                    Link(href="https://example.com", rel="self"),
                ],
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
        assert len(pub.get_acquisition_links()) == 1

    def test_from_publication(self):
        """Test creating OPDSPublication from Publication."""
        base = Publication(
            metadata=Metadata(title="Test Book"),
            links=[Link(href="https://example.com", rel="self")],
        )
        with pytest.raises(ValidationError):
            OPDSPublication.from_publication(base)


class TestContributorModel:
    """Tests for Contributor model."""

    def test_contributor_with_links(self):
        """Test contributor with links."""
        contributor = Contributor(
            name="Test Author",
            links=[Link(href="https://example.com/author", rel="self")],
        )
        assert contributor.name == "Test Author"
        assert len(contributor.links) == 1

    def test_contributor_with_sort_as(self):
        """Test contributor with sortAs."""
        contributor = Contributor(
            name="Doe, John",
            sortAs="Doe, John",
        )
        assert contributor.sortAs == "Doe, John"


class TestSeriesModel:
    """Tests for Series model."""

    def test_series_with_position(self):
        """Test series with position."""
        series = Series(
            name="Test Series",
            position=1,
        )
        assert series.name == "Test Series"
        assert series.position == 1


class TestBelongsToModel:
    """Tests for BelongsTo model."""

    def test_belongs_to_series(self):
        """Test belongs to series."""
        belongs = BelongsTo(
            series=Series(name="Test Series"),
        )
        assert belongs.series is not None
        assert belongs.series.name == "Test Series"

    def test_belongs_to_collection(self):
        """Test belongs to collection."""
        belongs = BelongsTo(
            collection="Test Collection",
        )
        assert belongs.collection == "Test Collection"
