"""OPDS 1.2 namespace constants and XML utilities."""

from __future__ import annotations

# Atom namespace
ATOM_NS = "http://www.w3.org/2005/Atom"
ATOM_PREFIX = "atom"

# Dublin Core namespace
DC_NS = "http://purl.org/dc/terms/"
DC_PREFIX = "dc"

# OPDS namespace
OPDS_NS = "http://opds-spec.org/2010/catalog"
OPDS_PREFIX = "opds"

# OpenSearch namespace
OPENSEARCH_NS = "http://a9.com/-/spec/opensearch/1.1/"
OPENSEARCH_PREFIX = "opensearch"

# Thrift namespace for counts
THRIFT_NS = "http://purl.org/syndication/thread/1.0"
THRIFT_PREFIX = "thr"

# Complete acquisition relation
CRAWLABLE_REL = "http://opds-spec.org/crawlable"

# Navigation relations
SUBSECTION_REL = "subsection"
SORT_NEW_REL = "http://opds-spec.org/sort/new"
SORT_POPULAR_REL = "http://opds-spec.org/sort/popular"
FEATURED_REL = "http://opds-spec.org/featured"
RECOMMENDED_REL = "http://opds-spec.org/recommended"

# Acquisition relations
ACQUISITION_REL = "http://opds-spec.org/acquisition"
OPEN_ACCESS_REL = "http://opds-spec.org/acquisition/open-access"
BORROW_REL = "http://opds-spec.org/acquisition/borrow"
BUY_REL = "http://opds-spec.org/acquisition/buy"
SAMPLE_REL = "http://opds-spec.org/acquisition/sample"
SUBSCRIBE_REL = "http://opds-spec.org/acquisition/subscribe"

# Image relations
IMAGE_REL = "http://opds-spec.org/image"
THUMBNAIL_REL = "http://opds-spec.org/image/thumbnail"

# User relations
SHELF_REL = "http://opds-spec.org/shelf"
SUBSCRIPTIONS_REL = "http://opds-spec.org/subscriptions"

# Feed types
NAVIGATION_TYPE = "application/atom+xml;profile=opds-catalog;kind=navigation"
ACQUISITION_TYPE = "application/atom+xml;profile=opds-catalog;kind=acquisition"
ENTRY_TYPE = "application/atom+xml;type=entry;profile=opds-catalog"


def make_clark_ns(tag: str, ns: str) -> str:
    """Create Clark notation tag name.

    Args:
        tag: Local tag name.
        ns: Namespace URI.

    Returns:
        Clark notation string.
    """
    return f"{{{ns}}}{tag}"


def get_namespace_map() -> dict[str, str]:
    """Get namespace mapping for XML parsing.

    Returns:
        Dictionary mapping prefixes to namespace URIs.
    """
    return {
        ATOM_PREFIX: ATOM_NS,
        DC_PREFIX: DC_NS,
        OPDS_PREFIX: OPDS_NS,
        OPENSEARCH_PREFIX: OPENSEARCH_NS,
        THRIFT_PREFIX: THRIFT_NS,
    }
