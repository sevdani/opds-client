"""Parser for OPDS 1.2 XML feeds."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Optional

from opds_client.opds12.exceptions import OPDSParseError, OPDSValidationError
from opds_client.opds12.models import (
    DublinCoreMetadata,
    Entry,
    FacetGroup,
    Feed,
    IndirectAcquisition,
    Link,
    Price,
)
from opds_client.opds12.namespace import (
    ATOM_NS,
    ATOM_PREFIX,
    DC_NS,
    DC_PREFIX,
    OPDS_NS,
    OPDS_PREFIX,
    OPENSEARCH_NS,
    OPENSEARCH_PREFIX,
    THRIFT_NS,
    THRIFT_PREFIX,
)


class OPDS12Parser:
    """Parser for OPDS 1.2 XML feeds."""

    NAMESPACES = {
        ATOM_PREFIX: ATOM_NS,
        DC_PREFIX: DC_NS,
        OPDS_PREFIX: OPDS_NS,
        OPENSEARCH_PREFIX: OPENSEARCH_NS,
        THRIFT_PREFIX: THRIFT_NS,
    }

    def __init__(self, strict: bool = True):
        """Initialize parser.

        Args:
            strict: If True, raise errors on validation failures.
                   If False, attempt to parse with warnings.
        """
        self.strict = strict
        self.warnings: list[str] = []

    def parse(self, xml_str: str | bytes) -> Feed:
        """Parse OPDS 1.2 XML feed.

        Args:
            xml_str: XML string or bytes to parse.

        Returns:
            Feed object.

        Raises:
            OPDSParseError: If XML parsing fails.
            OPDSValidationError: If validation fails.
        """
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            raise OPDSParseError(f"Invalid XML: {e}") from e

        return self._parse_feed(root)

    def parse_entry(self, xml_str: str | bytes) -> Entry:
        """Parse OPDS 1.2 XML entry.

        Args:
            xml_str: XML string or bytes to parse.

        Returns:
            Entry object.

        Raises:
            OPDSParseError: If XML parsing fails.
            OPDSValidationError: If validation fails.
        """
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            raise OPDSParseError(f"Invalid XML: {e}") from e

        return self._parse_entry(root)

    def _parse_feed(self, root: ET.Element) -> Feed:
        """Parse feed from XML element.

        Args:
            root: Root XML element.

        Returns:
            Feed object.
        """
        # Extract namespace from root tag
        if root.tag.startswith("{"):
            root.tag[1 : root.tag.find("}")]
        else:
            pass

        # Parse feed metadata
        title = self._get_text(root, "title", namespace=ATOM_NS)
        feed_id = self._get_text(root, "id", namespace=ATOM_NS)
        updated_str = self._get_text(root, "updated", namespace=ATOM_NS)
        updated = self._parse_datetime(updated_str)

        # Parse links
        links = self._parse_links(root, namespace=ATOM_NS)

        # Parse authors
        authors = self._parse_authors(root, namespace=ATOM_NS)

        # Parse Dublin Core metadata
        dc_metadata = self._parse_dc_metadata(root, namespace=DC_NS)
        dc_metadata_obj = dc_metadata if dc_metadata else None

        # Parse OpenSearch metadata
        total_results = self._get_int(root, "totalResults", namespace=OPENSEARCH_NS)
        items_per_page = self._get_int(root, "itemsPerPage", namespace=OPENSEARCH_NS)
        start_index = self._get_int(root, "startIndex", namespace=OPENSEARCH_NS) or 1

        # Parse entries
        entries = self._parse_entries(root, namespace=ATOM_NS)

        # Parse facets (links with facet relation)
        self._parse_facets(root, namespace=ATOM_NS)

        return Feed(
            id=feed_id or "",
            title=title or "",
            updated=updated or datetime.now(),
            links=links,
            authors=authors if authors else None,
            entries=entries if entries else None,
            totalResults=total_results,
            itemsPerPage=items_per_page,
            startIndex=start_index,
            dc_metadata=dc_metadata_obj,
        )

    def _parse_entries(self, root: ET.Element, namespace: str) -> list[Entry]:
        """Parse entry elements from feed.

        Args:
            root: Root XML element.
            namespace: Atom namespace.

        Returns:
            List of entries.
        """
        entries = []

        entry_elements = root.findall(f"{{{namespace}}}entry", self.NAMESPACES)

        for entry_elem in entry_elements:
            try:
                entry = self._parse_entry(entry_elem)
                entries.append(entry)
            except (OPDSValidationError, ValueError) as e:
                if self.strict:
                    raise
                self.warnings.append(f"Skipping invalid entry: {e}")

        return entries

    def _parse_entry(self, root: ET.Element) -> Entry:
        """Parse entry from XML element.

        Args:
            root: Root XML element.

        Returns:
            Entry object.
        """
        # Extract namespace from root tag
        if root.tag.startswith("{"):
            root.tag[1 : root.tag.find("}")]
        else:
            pass

        # Parse entry metadata
        entry_id = self._get_text(root, "id", namespace=ATOM_NS)
        title = self._get_text(root, "title", namespace=ATOM_NS)
        updated_str = self._get_text(root, "updated", namespace=ATOM_NS)
        updated = self._parse_datetime(updated_str)
        published_str = self._get_text(root, "published", namespace=ATOM_NS)
        published = self._parse_datetime(published_str) if published_str else None
        rights = self._get_text(root, "rights", namespace=ATOM_NS)
        summary = self._get_text(root, "summary", namespace=ATOM_NS)
        content = self._get_text(root, "content", namespace=ATOM_NS)

        # Parse links
        links = self._parse_links(root, namespace=ATOM_NS)

        # Parse authors
        authors = self._parse_authors(root, namespace=ATOM_NS)

        # Parse categories
        categories = self._parse_categories(root, namespace=ATOM_NS)

        # Parse Dublin Core metadata
        dc_metadata = self._parse_dc_metadata(root, namespace=DC_NS)
        dc_metadata_obj = dc_metadata if dc_metadata else None

        # Create entry
        entry = Entry(
            id=entry_id or "",
            title=title or "",
            updated=updated or datetime.now(),
            published=published,
            rights=rights,
            summary=summary,
            content=content,
            links=links,
            authors=authors if authors else None,
            categories=categories if categories else None,
            dc_metadata=dc_metadata_obj,
        )

        # Validate entry
        if self.strict:
            entry.model_validate(entry)

        return entry

    def _parse_links(self, root: ET.Element, namespace: str) -> list[Link]:
        """Parse link elements.

        Args:
            root: Root XML element.
            namespace: Atom namespace.

        Returns:
            List of links.
        """
        links = []

        link_elements = root.findall(f"{{{namespace}}}link", self.NAMESPACES)

        for link_elem in link_elements:
            link = self._parse_link(link_elem, namespace=ATOM_NS)
            links.append(link)

        return links

    def _parse_link(self, elem: ET.Element, namespace: str) -> Link:
        """Parse a single link element.

        Args:
            elem: Link XML element.
            namespace: Atom namespace.

        Returns:
            Link object.
        """
        href = elem.get("href")
        rel = elem.get("rel")
        title = elem.get("title")
        link_type = elem.get("type")

        # Parse OPDS-specific properties
        properties = self._parse_opds_properties(elem)

        link = Link(
            href=href or "",
            rel=rel,
            title=title,
            type=link_type,
            properties=properties if properties else None,
        )

        return link

    def _parse_opds_properties(self, elem: ET.Element) -> dict[str, Any]:
        """Parse OPDS-specific properties from link element.

        Args:
            elem: Link XML element.

        Returns:
            Dictionary of properties.
        """
        properties = {}

        # Parse price elements
        price_elements = elem.findall(f"{{{OPDS_NS}}}price", self.NAMESPACES)
        if price_elements:
            prices = []
            for price_elem in price_elements:
                price = Price(
                    value=price_elem.text or "",
                    currencycode=price_elem.get("currencycode", ""),
                )
                prices.append(price)
            properties["price"] = prices[0] if len(prices) == 1 else prices

        # Parse indirect acquisition elements
        indirect_elements = elem.findall(
            f"{{{OPDS_NS}}}indirectAcquisition", self.NAMESPACES
        )
        if indirect_elements:
            indirect_acq = []
            for indirect_elem in indirect_elements:
                indirect = self._parse_indirect_acquisition(indirect_elem)
                indirect_acq.append(indirect)
            properties["indirectAcquisition"] = indirect_acq  # type: ignore[assignment]

        # Parse facet group attributes
        facet_group = elem.get(f"{{{OPDS_NS}}}facetGroup")
        if facet_group:
            properties["facetGroup"] = facet_group  # type: ignore[assignment]

        active_facet = elem.get(f"{{{OPDS_NS}}}activeFacet")
        if active_facet is not None:
            properties["activeFacet"] = active_facet  # type: ignore[assignment]

        # Parse thr:count
        count = elem.get(f"{{{THRIFT_NS}}}count")
        if count:
            properties["count"] = int(count)  # type: ignore[assignment]

        return properties

    def _parse_indirect_acquisition(self, elem: ET.Element) -> IndirectAcquisition:
        """Parse indirect acquisition element.

        Args:
            elem: Indirect acquisition XML element.

        Returns:
            IndirectAcquisition object.
        """
        acq_type = elem.get("type", "")

        # Parse child indirect acquisitions
        children = []
        child_elements = elem.findall(
            f"{{{OPDS_NS}}}indirectAcquisition", self.NAMESPACES
        )
        for child_elem in child_elements:
            child = self._parse_indirect_acquisition(child_elem)
            children.append(child)

        return IndirectAcquisition(
            type=acq_type,
            child=children if children else None,
        )

    def _parse_authors(self, root: ET.Element, namespace: str) -> list[str]:
        """Parse author elements.

        Args:
            root: Root XML element.
            namespace: Atom namespace.

        Returns:
            List of author names.
        """
        authors = []

        author_elements = root.findall(f"{{{namespace}}}author", self.NAMESPACES)

        for author_elem in author_elements:
            name = self._get_text(author_elem, "name", namespace=ATOM_NS)
            if name:
                authors.append(name)

        return authors

    def _parse_categories(self, root: ET.Element, namespace: str) -> list[str]:
        """Parse category elements.

        Args:
            root: Root XML element.
            namespace: Atom namespace.

        Returns:
            List of category terms.
        """
        categories = []

        category_elements = root.findall(f"{{{namespace}}}category", self.NAMESPACES)

        for category_elem in category_elements:
            term = category_elem.get("term")
            if term:
                categories.append(term)

        return categories

    def _parse_dc_metadata(
        self, root: ET.Element, namespace: str
    ) -> Optional[DublinCoreMetadata]:
        """Parse Dublin Core metadata elements.

        Args:
            root: Root XML element.
            namespace: Dublin Core namespace.

        Returns:
            DublinCoreMetadata object or None.
        """
        dc_metadata: dict[str, Any] = {}

        dc_elements = [
            "identifier",
            "title",
            "creator",
            "contributor",
            "date",
            "type",
            "format",
            "language",
            "publisher",
            "description",
            "subject",
            "rights",
        ]

        for elem_name in dc_elements:
            dc_elem = root.find(f"{{{namespace}}}{elem_name}", self.NAMESPACES)
            if dc_elem is not None and dc_elem.text:
                if elem_name == "date":
                    try:
                        dc_metadata[elem_name] = datetime.fromisoformat(dc_elem.text)
                    except ValueError:
                        dc_metadata[elem_name] = None
                else:
                    dc_metadata[elem_name] = dc_elem.text

        if dc_metadata:
            return DublinCoreMetadata(**dc_metadata)

        return None

    def _parse_facets(self, root: ET.Element, namespace: str) -> list[FacetGroup]:
        """Parse facet groups from feed.

        Args:
            root: Root XML element.
            namespace: Atom namespace.

        Returns:
            List of facet groups.
        """
        facets = []
        facet_groups: dict[str, dict[str, Any]] = {}

        # Find all links with opds:facetGroup attribute
        link_elements = root.findall(f"{{{namespace}}}link", self.NAMESPACES)

        for link_elem in link_elements:
            facet_group_name = link_elem.get(f"{{{OPDS_NS}}}facetGroup")
            if facet_group_name:
                if facet_group_name not in facet_groups:
                    facet_groups[facet_group_name] = {
                        "links": [],
                        "active_facet": None,
                        "count": None,
                    }

                link = self._parse_link(link_elem, namespace=ATOM_NS)
                facet_groups[facet_group_name]["links"].append(link)

                # Check if this is the active facet
                active = link_elem.get(f"{{{OPDS_NS}}}activeFacet")
                if active == "true":
                    facet_groups[facet_group_name]["active_facet"] = link.rel

                # Get count
                count = link_elem.get(f"{{{THRIFT_NS}}}count")
                if count:
                    facet_groups[facet_group_name]["count"] = int(count)

        # Convert to FacetGroup objects
        for group_name, data in facet_groups.items():
            facets.append(
                FacetGroup(
                    title=group_name,
                    links=data["links"],
                    active_facet=data["active_facet"],
                    count=data["count"],
                )
            )

        return facets

    def _get_text(
        self,
        root: ET.Element,
        tag: str,
        namespace: str = "",
    ) -> Optional[str]:
        """Get text content of a child element.

        Args:
            root: Parent XML element.
            tag: Child element tag name.
            namespace: XML namespace.

        Returns:
            Text content or None.
        """
        if namespace:
            elem = root.find(f"{{{namespace}}}{tag}", self.NAMESPACES)
        else:
            elem = root.find(tag, self.NAMESPACES)

        if elem is not None and elem.text:
            return elem.text.strip()

        return None

    def _get_int(
        self,
        root: ET.Element,
        tag: str,
        namespace: str = "",
    ) -> Optional[int]:
        """Get integer value of a child element.

        Args:
            root: Parent XML element.
            tag: Child element tag name.
            namespace: XML namespace.

        Returns:
            Integer value or None.
        """
        text = self._get_text(root, tag, namespace=namespace)
        if text:
            try:
                return int(text)
            except ValueError:
                return None
        return None

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string.

        Args:
            date_str: Datetime string.

        Returns:
            datetime object or None.
        """
        if not date_str:
            return None

        # Try different formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None
