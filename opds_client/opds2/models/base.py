"""Base models for OPDS 2.0 specification."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class Price(BaseModel):
    """Price object for acquisition links."""

    currency: str = Field(..., min_length=3, max_length=3)
    value: float = Field(..., ge=0)

    @field_validator("currency")
    @classmethod
    def currency_must_be_valid(cls, v: str) -> str:
        """Validate ISO 4217 currency code format."""
        if not re.match(r"^[A-Z]{3}$", v):
            raise ValueError("Currency must be a 3-letter ISO 4217 code")
        return v


class IndirectAcquisition(BaseModel):
    """Indirect acquisition object for chained acquisition flows."""

    type: str = Field(..., alias="type")
    child: Optional[list["IndirectAcquisition"]] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class PriceObject(BaseModel):
    """Price object in properties."""

    price: Optional[Price] = Field(default=None, alias="price")
    indirect_acquisition: Optional[list[IndirectAcquisition]] = Field(
        default=None, alias="indirectAcquisition"
    )
    holds: Optional[dict[str, int]] = Field(default=None)
    copies: Optional[dict[str, int]] = Field(default=None)
    availability: Optional[dict[str, Any]] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class Link(BaseModel):
    """Link object as defined in OPDS 2.0 spec."""

    href: AnyHttpUrl | str
    rel: Optional[str | list[str]] = Field(default=None)
    title: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    templated: bool = Field(default=False)
    properties: Optional[PriceObject] = Field(default=None)
    _url: Optional[str] = None

    @model_validator(mode="after")
    def validate_link(self) -> "Link":
        """Validate link requirements."""
        if self.templated:
            href_str = (
                str(self.href) if isinstance(self.href, AnyHttpUrl) else self.href
            )
            if not re.search(r"\{[^}]+\}", href_str):
                raise ValueError("Templated links must contain URI template parameters")
        return self

    def is_navigation_link(self) -> bool:
        """Check if this link is a navigation link."""
        return self.rel in ["navigation", "section"] or (
            isinstance(self.rel, list) and "navigation" in self.rel
        )

    def is_search_link(self) -> bool:
        """Check if this link is a search link."""
        return self.rel == "search" or (
            isinstance(self.rel, list) and "search" in self.rel
        )

    def fill_template(self, **params: str | int | float) -> str:
        """Fill URI template with parameters."""
        if not self.templated:
            return str(self.href)

        href_str = str(self.href)
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in href_str:
                href_str = href_str.replace(placeholder, str(value))

        return href_str

    def get_query_params(self) -> dict[str, list[str]]:
        """Extract query parameters from URI template."""
        if not self.templated:
            return {}

        parsed = urlparse(str(self.href))
        query = parsed.query if parsed.query else ""
        template_params = re.findall(r"\{([^}]+)\}", query)
        return {p: [] for p in template_params}


class NavigationLink(Link):
    """Specialized link for navigation collections."""

    @model_validator(mode="after")
    def validate_navigation_link(self) -> "NavigationLink":
        """Navigation links must have a title."""
        if self.title is None:
            raise ValueError("Navigation links must have a title")
        return self


class Metadata(BaseModel):
    """Metadata object for collections and publications."""

    title: str
    identifier: Optional[str] = Field(default=None)
    modified: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default=None)
    language: Optional[str | list[str]] = Field(default=None)
    numberOfItems: Optional[int] = Field(default=None, alias="numberOfItems")
    itemsPerPage: Optional[int] = Field(default=None, alias="itemsPerPage")
    currentPage: Optional[int] = Field(default=None, alias="currentPage")
    properties: Optional[dict[str, Any]] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class ImageLink(Link):
    """Link object for images collection."""

    height: Optional[int] = Field(default=None, ge=0)
    width: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_image_link(self) -> "ImageLink":
        """Images must have a valid format."""
        valid_formats = [
            "image/jpeg",
            "image/avif",
            "image/webp",
            "image/jxl",
            "image/png",
            "image/gif",
        ]
        if self.type and self.type not in valid_formats:
            raise ValueError(f"Image type must be one of {valid_formats}")
        return self


class FacetLink(Link):
    """Link object for facet collections."""

    properties: Optional[dict[str, Any]] = Field(default=None)  # type: ignore[assignment]

    def is_active(self) -> bool:
        """Check if this facet link is currently active."""
        if not self.rel:
            return False
        if isinstance(self.rel, list):
            return "self" in self.rel
        return self.rel == "self"

    def get_number_of_items(self) -> Optional[int]:
        """Get the numberOfItems from properties."""
        if self.properties and isinstance(self.properties, dict):
            value = self.properties.get("numberOfItems")
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    return None
        return None
