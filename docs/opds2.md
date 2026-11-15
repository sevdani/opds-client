# OPDS 2.0 Guide

This guide covers using the OPDS 2.0 client for JSON-based OPDS catalogs.

## OPDS 2.0 Client

The `OPDSClient` class handles OPDS 2.0 feeds (JSON format).

### Fetching a Feed

```python
from opds_client import OPDSClient

client = OPDSClient()
feed = client.fetch_feed("https://example.com/opds")
```

### Feed Structure

An OPDS 2.0 feed contains:

- **Metadata**: Title, description, update timestamp
- **Links**: Self, first, previous, next, last, search links
- **Publications**: List of publication entries
- **Navigation**: Navigation links for browsing
- **Facets**: Facet groups for filtering
- **Groups**: Publication groups

### Navigation

```python
# Follow navigation by title
new_feed = client.follow_navigation(feed, "New Publications")

# Navigate facets
featured_feed = client.follow_facet(feed, "Category", "Featured")
```

### Pagination

```python
# Get next page
next_feed = client.get_next_page(feed)

# Get previous page
prev_feed = client.get_previous_page(feed)

# Get first/last page
first = client.get_first_page(feed)
last = client.get_last_page(feed)
```

### Search

```python
# Search the catalog
results = client.search(feed, "search query", title="My Book")

# Check if search is supported
if feed.get_search_link():
    results = client.search(feed, "query")
```

## Models

### OPDSFeed

Main feed class for OPDS 2.0:

```python
from opds_client.models import OPDSFeed, Metadata, Link

feed = OPDSFeed(
    metadata=Metadata(title="My Catalog"),
    links=[Link(href="https://example.com", rel="self")],
    publications=[...],
    navigation=[...],
)
```

### OPDSPublication

Individual publication entry:

```python
from opds_client.models import OPDSPublication, Metadata, Link

pub = OPDSPublication(
    metadata=Metadata(
        title="Test Book",
        author="Test Author",
    ),
    links=[
        Link(href="https://example.com", rel="self"),
        Link(href="https://example.com/download", rel="download"),
    ],
)
```

### Link Types

- **Link**: Basic link with href and relation
- **NavigationLink**: Link for navigation purposes
- **AcquisitionLink**: Link for acquiring publications

```python
from opds_client.models import Link, AcquisitionLink

# Basic link
link = Link(href="https://example.com", rel="self")

# Acquisition link
acq_link = AcquisitionLink(
    href="https://example.com/download",
    rel="download",
    type="application/epub+zip",
)
```
