"""Tests for acquisition models."""



from opds_client.models import (
    AcquisitionFlow,
    AcquisitionLink,
    AcquisitionManager,
)


class TestAcquisitionFlow:
    """Tests for AcquisitionFlow model."""

    def test_simple_flow(self):
        """Test simple acquisition flow."""
        link = AcquisitionLink(
            href="https://example.com/download",
            rel="download",
        )
        flow = AcquisitionFlow(link=link)
        assert flow.get_final_link() == link

    def test_chained_flow(self):
        """Test chained acquisition flow."""
        final_link = AcquisitionLink(
            href="https://example.com/final.epub",
            rel="download",
        )

        intermediate_link = AcquisitionLink(
            href="https://example.com/buy",
            rel="buy",
            properties={
                "indirectAcquisition": [
                    {"type": "application/epub+zip"}
                ]
            },
        )

        # Create a proper chain with the final link in the chain
        final_flow = AcquisitionFlow(link=final_link)
        intermediate_flow = AcquisitionFlow(
            link=intermediate_link,
            indirect_acquisition=[final_flow],
        )

        # The top flow should have the intermediate link
        top_flow = AcquisitionFlow(link=intermediate_link)

        # get_final_link should traverse the chain
        assert top_flow.get_final_link() == intermediate_link

        # And the intermediate flow with chain should return the final link
        assert intermediate_flow.get_final_link() == final_link


class TestAcquisitionManager:
    """Tests for AcquisitionManager."""

    def test_download_link(self):
        """Test getting download link."""
        link = AcquisitionLink(
            href="https://example.com/download",
            rel="download",
        )
        manager = AcquisitionManager(link)

        download = manager.get_open_access_link()
        assert download is not None

    def test_buy_link(self):
        """Test getting buy link."""
        link = AcquisitionLink(
            href="https://example.com/buy",
            rel="buy",
            properties={
                "price": {"currency": "USD", "value": 9.99}
            },
        )
        manager = AcquisitionManager(link)

        buy = manager.get_buy_link()
        assert buy is not None
        assert buy.get_price() is not None
        assert buy.get_price().currency == "USD"

    def test_borrow_link(self):
        """Test getting borrow link."""
        link = AcquisitionLink(
            href="https://example.com/borrow",
            rel="borrow",
        )
        manager = AcquisitionManager(link)

        borrow = manager.get_borrow_link()
        assert borrow is not None

    def test_subscribe_link(self):
        """Test getting subscribe link."""
        link = AcquisitionLink(
            href="https://example.com/subscribe",
            rel="subscribe",
        )
        manager = AcquisitionManager(link)

        subscribe = manager.get_subscribe_link()
        assert subscribe is not None

    def test_list_flows(self):
        """Test listing acquisition flows."""
        link = AcquisitionLink(
            href="https://example.com/buy",
            rel="buy",
            properties={
                "price": {"currency": "USD", "value": 9.99}
            },
        )
        manager = AcquisitionManager(link)

        flow = AcquisitionFlow(link=link)
        manager.add_flow(flow)

        assert len(manager.flows) == 1
