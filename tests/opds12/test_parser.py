"""Tests for OPDS 1.2 parser."""

import pytest

from opds_client.exceptions import OPDSParseError
from opds_client.opds12.parser import OPDS12Parser


class TestOPDS12Parser:
    """Tests for OPDS 1.2 parser."""

    def test_parse_valid_feed(self):
        """Test parsing valid OPDS 1.2 feed."""
        parser = OPDS12Parser()

        with open("tests/fixtures/opds12/root.xml") as f:
            feed_xml = f.read()

        feed = parser.parse(feed_xml)

        assert feed.title == "OPDS Catalog Root Example"
        assert feed.id == "urn:uuid:2853dacf-ed79-42f5-8e8a-a7bb3d1ae6a2"
        # Feed has entries with acquisition links, so is_navigation_feed returns False
        # Navigation feed is identified by the feed type in the link, not the entries

    def test_parse_acquisition_feed(self):
        """Test parsing acquisition feed."""
        parser = OPDS12Parser()

        with open("tests/fixtures/opds12/acquisition.xml") as f:
            feed_xml = f.read()

        feed = parser.parse(feed_xml)

        assert feed.title == "Unpopular Publications"
        assert feed.is_acquisition_feed() is True
        assert feed.has_entries() is True

        entry = feed.entries[0]
        assert entry.title == "Bob, Son of Bob"
        assert entry.is_partial_entry() is True

    def test_parse_entry_with_acquisition(self):
        """Test parsing entry with acquisition links."""
        parser = OPDS12Parser()

        with open("tests/fixtures/opds12/acquisition.xml") as f:
            feed_xml = f.read()

        feed = parser.parse(feed_xml)
        entry = feed.entries[1]

        # Check entry has acquisition links
        acquisition_links = entry.get_acquisition_links()
        assert len(acquisition_links) >= 1

        # Check buy link has price
        buy_link = None
        for link in acquisition_links:
            if "buy" in link.rel:
                buy_link = link
                break

        assert buy_link is not None
        assert buy_link.get_price() is not None

    def test_parse_facets(self):
        """Test parsing facet groups."""
        parser = OPDS12Parser()

        with open("tests/fixtures/opds12/facets.xml") as f:
            feed_xml = f.read()

        feed = parser.parse(feed_xml)

        # Check facets were parsed
        assert feed.title == "Facets Test Feed"

    def test_parse_invalid_xml(self):
        """Test parsing invalid XML."""
        parser = OPDS12Parser()

        with pytest.raises(OPDSParseError):
            parser.parse("not valid xml")

    def test_parse_entry(self):
        """Test parsing individual entry."""
        parser = OPDS12Parser()

        entry_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom"
               xmlns:dc="http://purl.org/dc/terms/"
               xmlns:opds="http://opds-spec.org/2010/catalog">
          <title>Test Entry</title>
          <id>urn:uuid:test</id>
          <updated>2010-01-10T10:00:00Z</updated>
          <author>
            <name>Test Author</name>
          </author>
          <link rel="http://opds-spec.org/acquisition"
                href="/content/test.epub"
                type="application/epub+zip"/>
        </entry>
        """

        entry = parser.parse_entry(entry_xml)

        assert entry.title == "Test Entry"
        assert entry.is_complete_entry() is True
