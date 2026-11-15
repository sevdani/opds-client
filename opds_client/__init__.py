"""OPDS Client Library supporting OPDS 1.2 and OPDS 2.0."""

# Version modules for organized access
import opds_client.opds2 as v2_0
import opds_client.opds12 as v1_2
from opds_client.opds2.client import OPDS2Client
from opds_client.opds12.client import OPDS12Client

__all__ = [
    "OPDS12Client",
    "OPDS2Client",
    "v1_2",
    "v2_0",
]
