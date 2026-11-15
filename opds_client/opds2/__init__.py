"""OPDS 2.0 Client Library."""

from opds_client.utils import merge_urls

from .client import OPDS2Client
from .exceptions import (
    OPDSHTTPError,
    OPDSNavigationError,
    OPDSParseError,
    OPDSValidationError,
    SearchError,
)
from .models import (
    AcquisitionLink,
    Facet,
    Group,
    Link,
    Metadata,
    NavigationLink,
    OPDSFeed,
    OPDSPublication,
    Publication,
)
from .parser import OPDS2Parser, URITemplateResolver

__all__ = [
    "OPDS2Client",
    "OPDS2Parser",
    "OPDSFeed",
    "OPDSPublication",
    "Link",
    "Metadata",
    "Publication",
    "NavigationLink",
    "Facet",
    "Group",
    "AcquisitionLink",
    "URITemplateResolver",
    "merge_urls",
    "OPDSHTTPError",
    "OPDSParseError",
    "OPDSValidationError",
    "OPDSNavigationError",
    "SearchError",
]
