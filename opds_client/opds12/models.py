"""Models for OPDS 1.2."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class Price(BaseModel):
    """OPDS 1.2 price element."""

    value: str = Field(..., description="Price value as text")
    currencycode: str = Field(
        ..., min_length=3, max_length=3, description="ISO 4217 currency code"
    )

    @field_validator("currencycode")
    @classmethod
    def validate_currencycode(cls, v: str) -> str:
        """Validate currency code format."""
        if not v.isupper() or len(v) != 3:
            raise ValueError("Currency code must be a 3-letter ISO 4217 code")
        return v


class IndirectAcquisition(BaseModel):
    """OPDS 1.2 indirect acquisition element."""

    type: str = Field(..., alias="type", description="MIME media type")
    child: Optional[list["IndirectAcquisition"]] = Field(
        default=None, description="Nested acquisitions"
    )

    model_config = ConfigDict(populate_by_name=True)


class Link(BaseModel):
    """OPDS 1.2 Atom link element."""

    href: str | AnyHttpUrl
    rel: Optional[str | list[str]] = Field(default=None, description="Link relation")
    title: Optional[str] = Field(default=None, description="Link title")
    type: Optional[str] = Field(default=None, description="MIME media type")
    properties: Optional[dict[str, Any]] = Field(
        default=None, description="Additional properties"
    )

    def is_acquisition_link(self) -> bool:
        """Check if this is an acquisition link."""
        if not self.rel:
            return False
        acquisition_prefixes = [
            "http://opds-spec.org/acquisition",
        ]
        if isinstance(self.rel, str):
            return any(self.rel.startswith(prefix) for prefix in acquisition_prefixes)
        return False

    def get_price(self) -> Optional[Price]:
        """Get price from properties."""
        if self.properties and "price" in self.properties:
            price_obj = self.properties["price"]
            if isinstance(price_obj, list):
                return price_obj[0] if price_obj else None
            if isinstance(price_obj, Price):
                return price_obj
            return None
        return None

    def get_indirect_acquisitions(self) -> list[IndirectAcquisition]:
        """Get indirect acquisitions from properties."""
        if self.properties and "indirectAcquisition" in self.properties:
            acq = self.properties["indirectAcquisition"]
            if isinstance(acq, list):
                return acq
            return [acq] if acq is not None else []
        return []


class AcquisitionLink(Link):
    """OPDS 1.2 acquisition link with price support."""

    @model_validator(mode="after")
    def validate_acquisition_link(self) -> "AcquisitionLink":
        """Validate acquisition link requirements."""
        if self.rel and "buy" in self.rel:
            if not self.properties or "price" not in self.properties:
                raise ValueError("Buy link must have a price")
        return self


class FacetGroup(BaseModel):
    """OPDS 1.2 facet group."""

    title: str = Field(..., description="Group title")
    links: list[Link] = Field(..., min_length=1, description="Facet links")
    active_facet: Optional[str] = Field(
        default=None, description="Currently active facet"
    )
    count: Optional[int] = Field(default=None, ge=0, description="Number of items")

    @model_validator(mode="after")
    def validate_facet_group(self) -> "FacetGroup":
        """Validate facet group."""
        if self.count is not None and self.count < 0:
            raise ValueError("Count must be non-negative")
        return self

    def get_active_facet(self) -> Optional[Link]:
        """Get the currently active facet."""
        if not self.active_facet:
            return None
        for link in self.links:
            if link.rel == self.active_facet:
                return link
        return None


class DublinCoreMetadata(BaseModel):
    """Dublin Core metadata elements."""

    identifier: Optional[str] = Field(
        default=None, description="Publication identifier"
    )
    title: Optional[str] = Field(default=None, description="Publication title")
    creator: Optional[str] = Field(
        default=None, alias="creator", description="Author/creator"
    )
    contributor: Optional[str] = Field(default=None, description="Contributor")
    date: Optional[datetime] = Field(default=None, description="Publication date")
    type: Optional[str] = Field(default=None, description="Resource type")
    format: Optional[str] = Field(default=None, description="File format")
    language: Optional[str] = Field(default=None, description="Language")
    publisher: Optional[str] = Field(default=None, description="Publisher")
    description: Optional[str] = Field(default=None, description="Description")
    subject: Optional[str] = Field(default=None, description="Subject/category")
    rights: Optional[str] = Field(default=None, description="Rights info")

    model_config = ConfigDict(populate_by_name=True)


class Entry(BaseModel):
    """OPDS 1.2 Atom entry element."""

    id: str = Field(..., description="Entry identifier")
    title: str = Field(..., description="Entry title")
    updated: datetime = Field(..., description="Last updated timestamp")
    links: list[Link] = Field(..., min_length=1, description="Entry links")
    authors: Optional[list[str]] = Field(default=None, description="Entry authors")
    categories: Optional[list[str]] = Field(
        default=None, description="Entry categories"
    )
    rights: Optional[str] = Field(default=None, description="Rights")
    published: Optional[datetime] = Field(default=None, description="Published date")
    summary: Optional[str] = Field(default=None, description="Summary/description")
    content: Optional[str] = Field(default=None, description="Full content")
    dc_metadata: Optional[DublinCoreMetadata] = Field(
        default=None, alias="dc_metadata", description="Dublin Core metadata"
    )

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_entry(self) -> "Entry":
        """Validate entry requirements."""
        if not self.id:
            raise ValueError("Entry must have an id")
        if not self.title:
            raise ValueError("Entry must have a title")
        if not self.updated:
            raise ValueError("Entry must have an updated timestamp")

        # Must have at least one acquisition link (for OPDS 1.2 entries)
        # Note: Navigation feed entries don't have acquisition links,
        #   but the Entry model is for Acquisition Feed entries
        # The parser will skip non-acquisition entries for navigation feeds
        # has_acquisition = any(link.is_acquisition_link() for link in self.links)
        # if not has_acquisition:
        #     raise ValueError("Entry must have at least one acquisition link")

        return self

    def get_self_link(self) -> Optional[Link]:
        """Get the self link."""
        for link in self.links:
            if link.rel == "self":
                return link
        return None

    def get_alternate_link(self) -> Optional[Link]:
        """Get the alternate link (for complete entries)."""
        for link in self.links:
            if link.rel == "alternate":
                return link
        return None

    def get_acquisition_links(self) -> list[AcquisitionLink]:
        """Get all acquisition links."""
        return [link for link in self.links if link.is_acquisition_link()]  # type: ignore[misc]

    def has_price(self) -> bool:
        """Check if any acquisition link has a price."""
        return any(
            link.get_price() for link in self.links if link.is_acquisition_link()
        )

    def is_complete_entry(self) -> bool:
        """Check if this is a complete entry (no alternate link)."""
        return self.get_alternate_link() is None

    def is_partial_entry(self) -> bool:
        """Check if this is a partial entry (has alternate link)."""
        return not self.is_complete_entry()


class Feed(BaseModel):
    """OPDS 1.2 Atom feed element."""

    id: str = Field(..., description="Feed identifier")
    title: str = Field(..., description="Feed title")
    updated: datetime = Field(..., description="Last updated timestamp")
    links: list[Link] = Field(..., min_length=1, description="Feed links")
    authors: Optional[list[str]] = Field(default=None, description="Feed authors")
    entries: Optional[list[Entry]] = Field(default=None, description="Feed entries")
    total_results: Optional[int] = Field(
        default=None, ge=0, alias="totalResults", description="Total results"
    )
    items_per_page: Optional[int] = Field(
        default=None, ge=1, alias="itemsPerPage", description="Items per page"
    )
    start_index: Optional[int] = Field(
        default=1, ge=1, alias="startIndex", description="Start index"
    )
    dc_metadata: Optional[DublinCoreMetadata] = Field(
        default=None, alias="dc_metadata", description="Dublin Core metadata"
    )

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_feed(self) -> "Feed":
        """Validate feed requirements."""
        if not self.id:
            raise ValueError("Feed must have an id")
        if not self.title:
            raise ValueError("Feed must have a title")
        if not self.updated:
            raise ValueError("Feed must have an updated timestamp")
        if not self.links:
            raise ValueError("Feed must have links")
        if self.total_results is not None and self.total_results < 0:
            raise ValueError("Total results must be non-negative")
        if self.items_per_page is not None and self.items_per_page < 1:
            raise ValueError("Items per page must be at least 1")
        return self

    def get_self_link(self) -> Optional[Link]:
        """Get the self link."""
        for link in self.links:
            if link.rel == "self":
                return link
        return None

    def get_start_link(self) -> Optional[Link]:
        """Get the start link (OPDS catalog root)."""
        for link in self.links:
            if link.rel == "start":
                return link
        return None

    def get_crawlable_link(self) -> Optional[Link]:
        """Get the crawlable link (complete acquisition feed)."""
        for link in self.links:
            if link.rel == "http://opds-spec.org/crawlable":
                return link
        return None

    def is_acquisition_feed(self) -> bool:
        """Check if this is an acquisition feed."""
        if not self.entries:
            return False
        return any(entry.links for entry in self.entries)

    def is_navigation_feed(self) -> bool:
        """Check if this is a navigation feed."""
        if not self.entries:
            return False
        return not self.is_acquisition_feed()

    def get_facets_by_group(self, group_name: str) -> Optional[FacetGroup]:
        """Get facets by group name."""
        # For now, return None - facets would need to be parsed from links
        return None

    def get_next_link(self) -> Optional[Link]:
        """Get the next pagination link."""
        for link in self.links:
            if link.rel == "next":
                return link
        return None

    def get_previous_link(self) -> Optional[Link]:
        """Get the previous pagination link."""
        for link in self.links:
            if link.rel == "previous":
                return link
        return None

    def has_entries(self) -> bool:
        """Check if feed has entries."""
        return self.entries is not None and len(self.entries) > 0
