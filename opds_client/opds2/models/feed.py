"""Feed and collection models for OPDS 2.0."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, model_validator

from opds_client.opds2.models.base import (
    FacetLink,
    ImageLink,
    Link,
    Metadata,
    NavigationLink,
)
from opds_client.opds2.models.publication import OPDSPublication


class Collection(BaseModel):
    """Base collection model."""

    metadata: Optional[Metadata] = Field(default=None)
    links: Optional[list[Link]] = Field(default=None)
    navigation: Optional[list[NavigationLink]] = Field(default=None)
    publications: Optional[list[OPDSPublication]] = Field(default=None)
    images: Optional[list[ImageLink]] = Field(default=None)
    facets: Optional[list["Facet"]] = Field(default=None)
    groups: Optional[list["Group"]] = Field(default=None)

    @model_validator(mode="after")
    def validate_collection(self) -> "Collection":
        """Validate collection requirements."""
        if self.metadata and self.metadata.numberOfItems is not None:
            if self.metadata.numberOfItems < 0:
                raise ValueError("numberOfItems must be non-negative")
        return self

    def get_self_link(self) -> Optional[Link]:
        """Get the self link."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "self" or (
                isinstance(link.rel, list) and "self" in link.rel
            ):
                return link
        return None

    def get_next_link(self) -> Optional[Link]:
        """Get the next pagination link."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "next" or (
                isinstance(link.rel, list) and "next" in link.rel
            ):
                return link
        return None

    def get_previous_link(self) -> Optional[Link]:
        """Get the previous pagination link."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel in ["previous", "prev"] or (
                isinstance(link.rel, list)
                and ("previous" in link.rel or "prev" in link.rel)
            ):
                return link
        return None

    def get_first_link(self) -> Optional[Link]:
        """Get the first pagination link."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "first" or (
                isinstance(link.rel, list) and "first" in link.rel
            ):
                return link
        return None

    def get_last_link(self) -> Optional[Link]:
        """Get the last pagination link."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "last" or (
                isinstance(link.rel, list) and "last" in link.rel
            ):
                return link
        return None

    def get_search_link(self) -> Optional[Link]:
        """Get the search link."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "search" or (
                isinstance(link.rel, list) and "search" in link.rel
            ):
                return link
        return None

    def get_link_by_rel(self, rel: str) -> Optional[Link]:
        """Get a link by relation.

        Args:
            rel: Link relation to find.

        Returns:
            Link object or None if not found.
        """
        if not self.links:
            return None
        for link in self.links:
            if link.rel == rel or (isinstance(link.rel, list) and rel in link.rel):
                return link
        return None

    def has_navigation(self) -> bool:
        """Check if this collection has navigation links."""
        return self.navigation is not None and len(self.navigation) > 0

    def has_publications(self) -> bool:
        """Check if this collection has publications."""
        return self.publications is not None and len(self.publications) > 0

    def has_facets(self) -> bool:
        """Check if this collection has facets."""
        return self.facets is not None and len(self.facets) > 0

    def has_groups(self) -> bool:
        """Check if this collection has groups."""
        return self.groups is not None and len(self.groups) > 0


class Facet(BaseModel):
    """Facet group model."""

    metadata: Metadata
    links: list[FacetLink]

    def get_active_facet(self) -> Optional[FacetLink]:
        """Get the currently active facet link."""
        for link in self.links:
            if link.is_active():
                return link
        return None

    def get_facet_by_title(self, title: str) -> Optional[FacetLink]:
        """Get a facet link by title."""
        for link in self.links:
            if link.title == title:
                return link
        return None


class Group(BaseModel):
    """Group model for organizing collections."""

    metadata: Metadata
    links: Optional[list[Link]] = Field(default=None)
    navigation: Optional[list[NavigationLink]] = Field(default=None)
    publications: Optional[list[OPDSPublication]] = Field(default=None)
    images: Optional[list[ImageLink]] = Field(default=None)
    facets: Optional[list[Facet]] = Field(default=None)
    groups: Optional[list["Group"]] = Field(default=None)

    @model_validator(mode="after")
    def validate_group(self) -> "Group":
        """Validate group requirements."""
        if not self.metadata.title:
            raise ValueError("Group must have a title")
        if self.metadata.numberOfItems is not None and self.metadata.numberOfItems < 0:
            raise ValueError("numberOfItems must be non-negative")
        return self

    def get_self_link(self) -> Optional[Link]:
        """Get the self link."""
        if not self.links:
            return None
        for link in self.links:
            if link.rel == "self" or (
                isinstance(link.rel, list) and "self" in link.rel
            ):
                return link
        return None

    def has_navigation(self) -> bool:
        """Check if this group has navigation links."""
        return self.navigation is not None and len(self.navigation) > 0

    def has_publications(self) -> bool:
        """Check if this group has publications."""
        return self.publications is not None and len(self.publications) > 0


class OPDSFeed(Collection):
    """OPDS 2.0 Feed (the root collection)."""

    @model_validator(mode="after")
    def validate_feed(self) -> "OPDSFeed":
        """Validate feed requirements."""
        if not self.metadata:
            raise ValueError("Feed must have metadata")
        if not self.metadata.title:
            raise ValueError("Feed must have a title")
        if not self.links:
            raise ValueError("Feed must have links")

        has_self = False
        for link in self.links:
            if link.rel == "self" or (
                isinstance(link.rel, list) and "self" in link.rel
            ):
                has_self = True
                break
        if not has_self:
            raise ValueError("Feed must have a self link")

        has_collection = False
        if self.navigation and len(self.navigation) > 0:
            has_collection = True
        if self.publications and len(self.publications) > 0:
            has_collection = True
        if self.groups and len(self.groups) > 0:
            has_collection = True
        if self.facets and len(self.facets) > 0:
            has_collection = True

        if not has_collection:
            raise ValueError(
                "Feed must contain at least one collection " +
                "(navigation, publications, groups, or facets)"
            )

        return self

    def is_searchable(self) -> bool:
        """Check if this feed supports search."""
        return self.get_search_link() is not None

    def get_facets_by_title(self, title: str) -> Optional[Facet]:
        """Get a facet by title from nested groups."""
        if self.facets:
            for facet in self.facets:
                if facet.metadata.title == title:
                    return facet
        if self.groups:
            for group in self.groups:
                if group.facets:
                    for facet in group.facets:
                        if facet.metadata.title == title:
                            return facet
        return None
