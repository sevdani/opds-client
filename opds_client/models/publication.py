"""Publication models for OPDS 2.0."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from opds_client.models.base import (
    ImageLink,
    IndirectAcquisition,
    Link,
    Metadata,
    Price,
)


class Contributor(BaseModel):
    """Contributor metadata (author, editor, etc.)."""

    name: str
    identifier: Optional[str] = Field(default=None)
    sortAs: Optional[str] = Field(default=None, alias="sortAs")
    links: Optional[list[Link]] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class Series(BaseModel):
    """Series metadata."""

    name: str
    position: Optional[int] = Field(default=None, ge=1)
    links: Optional[list[Link]] = Field(default=None)


class BelongsTo(BaseModel):
    """BelongsTo metadata (series and collection)."""

    series: Optional[Series] = Field(default=None)
    collection: Optional[str] = Field(default=None)


class AcquisitionLink(Link):
    """Specialized link for acquisition."""

    RELATIONS: ClassVar[list[str]] = [
        "acquisition",
        "borrow",
        "buy",
        "download",
        "preview",
        "subscribe",
    ]

    @field_validator("rel")
    @classmethod
    def validate_acquisition_rel(
        cls, v: str | list[str] | None
    ) -> str | list[str] | None:
        """Validate acquisition relation."""
        if v is None:
            return v

        valid_rels = cls.RELATIONS + ["self", "http://opds-spec.org/acquisition"]

        if isinstance(v, str):
            if v not in valid_rels:
                raise ValueError(f"Invalid acquisition relation: {v}")
        elif isinstance(v, list):
            for rel in v:
                if rel not in valid_rels:
                    raise ValueError(f"Invalid acquisition relation: {rel}")

        return v

    def get_price(self) -> Optional[Price]:
        """Extract price from properties."""
        if self.properties and self.properties.price:
            return self.properties.price
        return None

    def get_indirect_acquisitions(self) -> list[IndirectAcquisition]:
        """Extract indirect acquisitions from properties."""
        if self.properties and self.properties.indirect_acquisition:
            return self.properties.indirect_acquisition
        return []

    def is_open_access(self) -> bool:
        """Check if this is an open access acquisition."""
        return self.rel in ["download", "preview"] or (
            isinstance(self.rel, list)
            and ("download" in self.rel or "preview" in self.rel)
        )


class Publication(BaseModel):
    """Base Publication model (Readium Web Publication)."""

    metadata: Metadata
    links: list[Link]
    images: Optional[list[ImageLink]] = Field(default=None)
    readingOrder: Optional[list[Link]] = Field(default=None)
    toc: Optional[list[Link]] = Field(default=None)
    resources: Optional[list[Link]] = Field(default=None)
    linksFrom: Optional[list[Link]] = Field(default=None)
    pubDate: Optional[datetime] = Field(default=None, alias="pubDate")
    modified: Optional[datetime] = Field(default=None, alias="modified")
    duration: Optional[float] = Field(default=None, ge=0)
    language: Optional[str | list[str]] = Field(default=None)
    numberOfPages: Optional[int] = Field(default=None, ge=1)
    mediaType: Optional[str] = Field(default=None, alias="mediaType")
    belongsTo: Optional[BelongsTo] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_publication(self) -> "Publication":
        """Validate publication requirements."""
        if not self.metadata.title:
            raise ValueError("Publication must have a title")
        if not self.links:
            raise ValueError("Publication must have at least one link")
        return self

    def get_self_link(self) -> Optional[Link]:
        """Get the self link."""
        for link in self.links:
            if link.rel == "self" or (
                isinstance(link.rel, list) and "self" in link.rel
            ):
                return link
        return None

    def get_image_by_type(self, image_type: str) -> Optional[ImageLink]:
        """Get an image by type."""
        if not self.images:
            return None
        for image in self.images:
            if image.type == image_type:
                return image
        return None

    def get_acquisition_links(self) -> list[Link]:
        """Get all acquisition links."""
        acquisition_links: list[Link] = []
        for link in self.links:
            if isinstance(link, AcquisitionLink):
                acquisition_links.append(link)
            elif link.rel in AcquisitionLink.RELATIONS or (
                isinstance(link.rel, list)
                and any(r in AcquisitionLink.RELATIONS for r in link.rel)
            ):
                acquisition_links.append(link)
        return acquisition_links


class OPDSPublication(Publication):
    """OPDS Publication (simplified Web Publication)."""

    @model_validator(mode="after")
    def validate_opds_publication(self) -> "OPDSPublication":
        """Validate OPDS publication requirements."""
        super().validate_publication()  # type: ignore[operator]

        has_acquisition = False
        for link in self.links:
            if link.rel in AcquisitionLink.RELATIONS or (
                isinstance(link.rel, list)
                and any(r in AcquisitionLink.RELATIONS for r in link.rel)
            ):
                has_acquisition = True
                break

        if not has_acquisition:
            raise ValueError("OPDS Publication must have at least one acquisition link")

        return self

    @classmethod
    def from_publication(cls, publication: Publication) -> "OPDSPublication":
        """Create OPDSPublication from Publication."""
        return cls(
            metadata=publication.metadata,
            links=publication.links,
            images=publication.images,
            readingOrder=publication.readingOrder,
            toc=publication.toc,
            resources=publication.resources,
            linksFrom=publication.linksFrom,
            pubDate=publication.pubDate,
            modified=publication.modified,
            duration=publication.duration,
            language=publication.language,
            numberOfPages=publication.numberOfPages,
            mediaType=publication.mediaType,
            belongsTo=publication.belongsTo,
        )
