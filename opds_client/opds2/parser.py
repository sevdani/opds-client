"""Parser for OPDS 2.0 JSON feeds."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from opds_client.opds2.exceptions import (
    OPDSParseError,
    OPDSValidationError,
)
from opds_client.opds2.models.base import (
    Link,
    NavigationLink,
)
from opds_client.opds2.models.feed import Facet, Group, OPDSFeed
from opds_client.opds2.models.publication import OPDSPublication


class OPDS2Parser:
    """Parser for OPDS 2.0 JSON feeds."""

    def __init__(self, strict: bool = True):
        """Initialize parser.

        Args:
            strict: If True, raise errors on validation failures.
                   If False, attempt to parse with warnings.
        """
        self.strict = strict
        self.warnings: list[str] = []

    def parse(self, json_str: str | bytes) -> OPDSFeed:
        """Parse OPDS 2.0 JSON feed.

        Args:
            json_str: JSON string or bytes to parse.

        Returns:
            OPDSFeed object.

        Raises:
            OPDSParseError: If JSON parsing fails.
            OPDSValidationError: If validation fails.
            InvalidOPDSFeedError: If the feed doesn't meet OPDS 2.0 requirements.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise OPDSParseError(f"Invalid JSON: {e}") from e

        return self.parse_dict(data)

    def parse_dict(self, data: dict[str, Any]) -> OPDSFeed:
        """Parse OPDS 2.0 feed from dictionary.

        Args:
            data: Dictionary containing OPDS feed data.

        Returns:
            OPDSFeed object.
        """
        return self._parse_feed(data)

    def _parse_feed(self, data: dict[str, Any]) -> OPDSFeed:
        """Parse feed from dictionary.

        Args:
            data: Dictionary containing feed data.

        Returns:
            OPDSFeed object.
        """
        try:
            feed = OPDSFeed.model_validate(data)
            return feed
        except ValidationError as e:
            if self.strict:
                raise OPDSValidationError(f"Feed validation failed: {e}") from e

            self.warnings.extend(str(err) for err in e.errors())
            # In non-strict mode, parse without strict validation
            # But still need to handle the validation for empty collections
            return self._parse_feed_loose(data)

    def _parse_feed_loose(self, data: dict[str, Any]) -> OPDSFeed:
        """Parse feed loosely, ignoring validation errors.

        Args:
            data: Dictionary containing feed data.

        Returns:
            OPDSFeed object (possibly incomplete).
        """
        metadata = data.get("metadata", {})

        links = []
        for link_data in data.get("links", []):
            try:
                link = Link.model_validate(link_data)
                links.append(link)
            except ValidationError:
                self.warnings.append(f"Skipping invalid link: {link_data}")

        navigation = []
        for nav_data in data.get("navigation", []):
            try:
                nav_link = NavigationLink.model_validate(nav_data)
                navigation.append(nav_link)
            except ValidationError:
                self.warnings.append(f"Skipping invalid navigation link: {nav_data}")

        publications = []
        for pub_data in data.get("publications", []):
            try:
                pub = OPDSPublication.model_validate(pub_data)
                publications.append(pub)
            except ValidationError:
                self.warnings.append(f"Skipping invalid publication: {pub_data}")

        groups = []
        for group_data in data.get("groups", []):
            try:
                group = Group.model_validate(group_data)
                groups.append(group)
            except ValidationError:
                self.warnings.append(f"Skipping invalid group: {group_data}")

        facets = []
        for facet_data in data.get("facets", []):
            try:
                facet = Facet.model_validate(facet_data)
                facets.append(facet)
            except ValidationError:
                self.warnings.append(f"Skipping invalid facet: {facet_data}")

        # Create feed without validation - allow empty collections
        metadata_obj = metadata if metadata else {"title": "Unknown"}
        return OPDSFeed(
            metadata=metadata_obj,  # type: ignore[arg-type]
            links=links,
            navigation=navigation if navigation else None,
            publications=publications if publications else None,
            groups=groups if groups else None,
            facets=facets if facets else None,
        )

    def parse_publication(self, json_str: str | bytes) -> OPDSPublication:
        """Parse OPDS 2.0 publication from JSON.

        Args:
            json_str: JSON string or bytes to parse.

        Returns:
            OPDSPublication object.

        Raises:
            OPDSParseError: If JSON parsing fails.
            OPDSValidationError: If validation fails.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise OPDSParseError(f"Invalid JSON: {e}") from e

        return self.parse_publication_dict(data)

    def parse_publication_dict(self, data: dict[str, Any]) -> OPDSPublication:
        """Parse publication from dictionary.

        Args:
            data: Dictionary containing publication data.

        Returns:
            OPDSPublication object.
        """
        try:
            pub = OPDSPublication.model_validate(data)
            return pub
        except ValidationError as e:
            if self.strict:
                raise OPDSValidationError(f"Publication validation failed: {e}") from e

            self.warnings.append(f"Publication validation failed: {e}")
            raise OPDSValidationError(f"Publication validation failed: {e}") from e


class URITemplateResolver:
    """Resolver for URI templates."""

    @staticmethod
    def resolve(template: str, **params: str | int | float) -> str:
        """Resolve URI template with parameters.

        Args:
            template: URI template string.
            **params: Parameters to substitute.

        Returns:
            Resolved URI string.

        Raises:
            ValueError: If required parameters are missing.
        """
        result = template

        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))

        missing = [
            p
            for p in URITemplateResolver._extract_params(template)
            if f"{{{p}}}" in result
        ]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        return result

    @staticmethod
    def fill_template(template: str, **params: str | int | float) -> str:
        """Fill URI template with parameters, leaving missing params unfilled.

        Args:
            template: URI template string.
            **params: Parameters to substitute.

        Returns:
            Filled URI string.
        """
        result = template

        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))

        return result

    @staticmethod
    def _extract_params(template: str) -> list[str]:
        """Extract parameter names from template.

        Args:
            template: URI template string.

        Returns:
            List of parameter names.
        """
        import re

        matches = re.findall(r"\{([^}]+)\}", template)
        params = []
        for match in matches:
            if match.startswith("?"):
                match = match[1:]
            params.extend(match.split(","))
        return params
