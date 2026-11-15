# OPDS 1.2 Guide

This guide covers using the OPDS 1.2 client for Atom/XML-based OPDS catalogs.

## OPDS 1.2 Client

The `OPDS12Client` class handles OPDS 1.2 feeds (Atom/XML format).

### Fetching a Feed

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")
```

### Feed Structure

An OPDS 1.2 feed contains:

- **Title**: Feed title
- **ID**: Feed identifier
- **Updated**: Last update timestamp
- **Entries**: List of publication entries
- **Links**: Feed-level links

### Navigation

```python
# Get start link (catalog root)
start_link = feed.get_start_link()

# Get self link
self_link = feed.get_self_link()

# Get next page
next_feed = client.get_next_page(feed)

# Get previous page
prev_feed = client.get_previous_page(feed)
```

### Acquisition Links

```python
# Get acquisition links from entries
entry = feed.entries[0]
acq_links = entry.get_acquisition_links()

# Follow specific acquisition type
buy_link = client.follow_acquisition(entry, acquisition_type="buy")
if buy_link:
    price = buy_link.get_price()
    print(f"Price: {price.currencycode} {price.value}")
```

## Models

### Feed

```python
from opds_client.opds12.models import Feed, Link, Entry

feed = Feed(
    id="urn:uuid:feed",
    title="OPDS 1.2 Feed",
    updated="2010-01-10T10:00:00Z",
    links=[Link(href="https://example.com", rel="self")],
    entries=[...],
)
```

### Entry

```python
from opds_client.opds12.models import Entry, Link, Price

entry = Entry(
    id="urn:uuid:test",
    title="Test Entry",
    updated="2010-01-10T10:00:00Z",
    authors=["Test Author"],
    links=[
        Link(
            href="https://example.com",
            rel="http://opds-spec.org/acquisition",
            type="application/epub+zip",
        ),
    ],
)
```

### Link Types

- **Link**: Basic link with href and relation
- **AcquisitionLink**: Link with acquisition properties

```python
from opds_client.opds12.models import Link, AcquisitionLink

# Basic link
link = Link(
    href="https://example.com",
    rel="http://opds-spec.org/acquisition",
    type="application/epub+zip",
)

# Acquisition link with price
acq_link = AcquisitionLink(
    href="https://example.com/buy",
    rel="http://opds-spec.org/acquisition/buy",
    properties={"price": Price(value="19.99", currencycode="USD")},
)
```

### Facet Groups

```python
# Get facet groups
facet_groups = feed.facets or []

# Navigate facets
for group in facet_groups:
    print(f"Group: {group.title}")
    for link in group.links or []:
        print(f"  - {link.title}")
```
