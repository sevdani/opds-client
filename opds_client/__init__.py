"""OPDS Client Library supporting OPDS 1.2 and OPDS 2.0."""

from opds_client.opds2 import (
    AcquisitionLink,
    Facet,
    Group,
    Link,
    Metadata,
    NavigationLink,
    OPDS2Client,
    OPDSFeed,
    OPDSPublication,
    Publication,
)
from opds_client.opds12 import OPDS12Client
from opds_client.opds12.models import (
    Entry as OPDS12Entry,
)
from opds_client.opds12.models import (
    FacetGroup,
)
from opds_client.opds12.models import (
    Feed as OPDS12Feed,
)
from opds_client.opds12.models import (
    Link as OPDS12Link,
)
from opds_client.opds12.parser import OPDS12Parser

__all__ = [
    "OPDS2Client",
    "Link",
    "Metadata",
    "Publication",
    "OPDSPublication",
    "OPDSFeed",
    "NavigationLink",
    "Facet",
    "Group",
    "AcquisitionLink",
    "OPDS12Client",
    "OPDS12Feed",
    "OPDS12Entry",
    "OPDS12Link",
    "FacetGroup",
    "OPDS12Parser",
]
