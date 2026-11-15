"""Acquisition models for OPDS 2.0."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from opds_client.opds2.models.base import Link


class AcquisitionFlow(BaseModel):
    """Represents an acquisition flow with multiple steps."""

    link: Link
    indirect_acquisition: Optional[list["AcquisitionFlow"]] = Field(
        default=None, alias="indirectAcquisition"
    )

    model_config = ConfigDict(populate_by_name=True)

    def get_final_link(self) -> Link:
        """Get the final link in the acquisition chain.

        Returns the deepest link in the indirect acquisition chain.
        If there are no indirect acquisitions, returns the current link.
        """
        if not self.indirect_acquisition:
            return self.link

        current = self
        while current.indirect_acquisition:
            current = current.indirect_acquisition[0]
        return current.link


class AcquisitionManager:
    """Manager for handling acquisition flows."""

    def __init__(self, link: Link):
        """Initialize with an acquisition link."""
        self.link = link
        self.flows: list[AcquisitionFlow] = []

    def add_flow(self, flow: AcquisitionFlow) -> None:
        """Add an acquisition flow."""
        self.flows.append(flow)

    def get_open_access_link(self) -> Optional[Link]:
        """Get an open access link if available."""
        if self.link.rel == "open-access":
            return self.link
        return None

    def get_buy_link(self) -> Optional[Link]:
        """Get a buy link if available."""
        if self.link.rel == "buy" or (
            isinstance(self.link.rel, list) and "buy" in self.link.rel
        ):
            return self.link
        return None

    def get_borrow_link(self) -> Optional[Link]:
        """Get a borrow link if available."""
        if self.link.rel == "borrow" or (
            isinstance(self.link.rel, list) and "borrow" in self.link.rel
        ):
            return self.link
        return None

    def get_subscribe_link(self) -> Optional[Link]:
        """Get a subscribe link if available."""
        if self.link.rel == "subscribe" or (
            isinstance(self.link.rel, list) and "subscribe" in self.link.rel
        ):
            return self.link
        return None

    def get_download_link(self) -> Optional[Link]:
        """Get a download link if available."""
        if self.link.rel == "download" or (
            isinstance(self.link.rel, list) and "download" in self.link.rel
        ):
            return self.link
        return None
