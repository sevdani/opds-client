"""OPDS 1.2 Client Library."""

from opds_client.opds12.client import OPDS12Client
from opds_client.opds12.models import (
    Entry,
    FacetGroup,
    Feed,
    Link,
)
from opds_client.opds12.parser import OPDS12Parser

__all__ = [
    "OPDS12Client",
    "Feed",
    "Entry",
    "Link",
    "FacetGroup",
    "OPDS12Parser",
]
