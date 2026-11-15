# OPDS Client

<div align="center">
<img src="https://raw.githubusercontent.com/sevdani/opds-client/refs/heads/main/docs/assets/logo.svg" width="150" />

# opds-client

A Python library for working with OPDS catalogs, supporting both [OPDS 1.2](https://specs.opds.io/opds-1.2) (Atom/XML) and [OPDS 2.0](https://specs.opds.io/opds-2.0) (JSON) specifications.

[![PyPI version](https://img.shields.io/pypi/v/opds-client)](https://pypi.org/project/opds-client)
[![PyPI downloads](https://img.shields.io/pypi/dm/opds-client)](https://pypi.org/project/opds-client)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI - Mainline](https://github.com/sevdani/opds-client/actions/workflows/mainline.yml/badge.svg)](https://github.com/sevdani/opds-client/actions/workflows/mainline.yml)
[![CI - Features](https://github.com/sevdani/opds-client/actions/workflows/features.yml/badge.svg)](https://github.com/sevdani/opds-client/actions/workflows/features.yml)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#features) · [Installation](#installation) · [Quick Start](#quick-start) · [Authentication](#authentication) · [Models](#models) · [Usage Examples](#usage-examples) · [OPDS 1.2 vs OPDS 2.0](#opds-12-vs-opds-20) · [Testing](#testing) · [Project Structure](#project-structure) · [License](#license)

</div>

---

## Features

### OPDS 2.0 (JSON)
- ✅ Parse OPDS 2.0 feeds and publications
- ✅ Validate against OPDS 2.0 specification
- ✅ Navigate navigation, publications, groups, and facets collections
- ✅ Handle pagination (first, previous, next, last links)
- ✅ Search catalogs with URI template resolution
- ✅ Work with acquisition links (download, buy, borrow, etc.)
- ✅ HTTP error handling with retries
- ✅ Pydantic models for type safety

### OPDS 1.2 (Atom/XML)
- ✅ Parse OPDS 1.2 Atom feeds and entries
- ✅ Dublin Core metadata support
- ✅ Navigation and Acquisition feeds
- ✅ Facet groups with active facets and item counts
- ✅ Acquisition links with prices and indirect acquisitions
- ✅ OpenSearch integration
- ✅ Multiple acquisition relations (buy, borrow, subscribe, etc.)

## Installation

```bash
pip install opds-client
```

## Quick Start

### OPDS 2.0 (JSON)

```python
from opds_client import OPDSClient

# Create a client
client = OPDSClient()

# Fetch a feed
feed = client.fetch_feed("https://example.com/opds")

# Access feed metadata
print(f"Title: {feed.metadata.title}")
print(f"Publications: {len(feed.publications or [])}")

# Navigate navigation links
for nav in feed.navigation or []:
    print(f"- {nav.title}: {nav.href}")

# Search
results = client.search(feed, "query")
```

### OPDS 1.2 (Atom/XML)

```python
from opds_client import OPDS12Client

# Create a client for OPDS 1.2
client = OPDS12Client()

# Fetch a feed (XML format)
feed = client.fetch_feed("https://example.com/opds.xml")

# Access feed metadata
print(f"Title: {feed.title}")
print(f"Entries: {len(feed.entries or [])}")

# Navigate navigation links
start_link = feed.get_start_link()

# Get acquisition links from entries
if feed.entries:
    entry = feed.entries[0]
    acq_links = entry.get_acquisition_links()
```

## Using Base URL (Origin)

Both OPDS 1.2 and OPDS 2.0 clients support setting a base URL (origin) that will be automatically prepended to relative URLs. This is useful when working with catalogs that use relative paths.

### OPDS 2.0 Example

```python
from opds_client import OPDSClient

# Create client with origin
client = OPDSClient(origin="https://example.com")

# Fetch feed with relative path
feed = client.fetch_feed("/catalog")  # → https://example.com/catalog

# Absolute URLs are used as-is
feed = client.fetch_feed("https://other.com/catalog")  # → https://other.com/catalog
```

### OPDS 1.2 Example

```python
from opds_client import OPDS12Client

# Create client with origin
client = OPDS12Client(origin="https://api.example.com")

# Fetch feed with relative path
feed = client.fetch_feed("/opds.xml")  # → https://api.example.com/opds.xml

# Navigation links with origin
start_link = feed.get_start_link()
if start_link:
    # The client automatically prepends the origin to relative URLs
    root_feed = client.get_start_link(feed)
```


## Authentication

Both OPDS 1.2 and OPDS 2.0 clients support HTTP Basic Authentication.

### Basic Auth with Username/Password

```python
from opds_client import OPDSClient

# For OPDS 2.0
client = OPDSClient(username="your_username", password="your_password")
feed = client.fetch_feed("https://example.com/opds")

# For OPDS 1.2
client = OPDS12Client(username="your_username", password="your_password")
feed = client.fetch_feed("https://example.com/opds.xml")
```

### Custom Auth Objects

For advanced authentication scenarios (Digest Auth, Bearer tokens, custom auth):

```python
from opds_client import OPDSClient
from requests.auth import HTTPDigestAuth, HTTPBasicAuth

# Digest authentication
client = OPDSClient(auth=HTTPDigestAuth("username", "password"))
feed = client.fetch_feed("https://example.com/opds")

# Custom auth (e.g., with session tokens)
class CustomAuth:
    def __call__(self, r):
        r.headers["X-Custom-Token"] = "your-token"
        return r

client = OPDSClient(auth=CustomAuth())
feed = client.fetch_feed("https://example.com/opds")
```

## Models

### OPDS 2.0 Models

#### Link

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

#### OPDS 1.2 Models

##### Link

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

##### Entry

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

##### Feed

```python
from opds_client.opds12.models import Feed, Link, Entry

feed = Feed(
    id="urn:uuid:feed",
    title="OPDS 1.2 Feed",
    updated="2010-01-10T10:00:00Z",
    links=[Link(href="https://example.com", rel="self")],
    entries=[entry],
)
```

### Publication (OPDS 2.0)

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

### Feed (OPDS 2.0)

```python
from opds_client.models import OPDSFeed

# Feed with collections
feed = OPDSFeed(
    metadata=Metadata(title="My Catalog"),
    links=[Link(href="https://example.com", rel="self")],
    navigation=[...],
    publications=[...],
    facets=[...],
    groups=[...],
)
```

## Usage Examples

### OPDS 2.0 Examples

#### Navigation

```python
from opds_client import OPDSClient

client = OPDSClient()
feed = client.fetch_feed("https://example.com/opds")

# Follow navigation by title
new_feed = client.follow_navigation(feed, "New Publications")

# Navigate facets
featured_feed = client.follow_facet(feed, "Category", "Featured")
```

#### OPDS 1.2 Examples

##### Navigation

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")

# Get start link (catalog root)
start_link = feed.get_start_link()

# Get self link
self_link = feed.get_self_link()

# Get next page
next_feed = client.get_next_page(feed)
```

### Pagination

```python
```python
# Get next page
next_feed = client.get_next_page(feed)

# Get previous page
prev_feed = client.get_previous_page(feed)

# Get first/last page
first = client.get_first_page(feed)
last = client.get_last_page(feed)
```

### OPDS 1.2 Pagination

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")

# Get next page
next_feed = client.get_next_page(feed)

# Get previous page  
prev_feed = client.get_previous_page(feed)

# Get catalog root
root_feed = client.get_start_link(feed)
```

### Search

```python
```python
# Search the catalog
results = client.search(feed, "search query", title="My Book")

# Check if search is supported
if feed.is_searchable():
    results = client.search(feed, "query")
```

### OPDS 1.2 Acquisition

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")

# Get acquisition links from entries
entry = feed.entries[0]
acq_links = entry.get_acquisition_links()

# Follow specific acquisition type
buy_link = client.follow_acquisition(entry, acquisition_type="buy")
if buy_link:
    price = buy_link.get_price()
    print(f"Price: {price.currencycode} {price.value}")
```

### Acquisition

```python
from opds_client.models import AcquisitionManager

```python
# Get acquisition links
pub = client.fetch_publication("https://example.com/publication")
acq_links = pub.get_acquisition_links()

# Use acquisition manager
manager = AcquisitionManager(acq_links[0])

# Check for open access
if manager.get_open_access_link():
    # Download directly
    pass

# Check for buy link
buy_link = manager.get_buy_link()
if buy_link:
    price = buy_link.get_price()
    print(f"Price: {price.currency} {price.value}")
```

## OPDS 1.2 vs OPDS 2.0

| Feature | OPDS 1.2 | OPDS 2.0 |
|---------|----------|----------|
| Format | Atom/XML | JSON |
| Parser | `OPDS12Parser` | `OPDS2Parser` |
| Client | `OPDS12Client` | `OPDS2Client` |
| Feed Type | `Feed` | `OPDSFeed` |
| Entry Type | `Entry` | `OPDSPublication` |
| Metadata | Dublin Core + Atom | JSON-LD (schema.org) |
| Acquisition Links | XML `opds:price` | JSON `properties.price` |

Choose the appropriate client based on your catalog's OPDS version.

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=opds_client

# Run type checks
mypy opds_client

# Run linter
ruff check .

# Format code
ruff format .
```

## Project Structure

```
opds_client/
├── __init__.py          # Package exports (OPDS 1.2 & 2.0)
├── client.py            # OPDS 2.0 Client
├── parser.py            # JSON parsing/validation (OPDS 2.0)
├── exceptions.py        # Custom exceptions
├── utils.py             # Utility functions
├── models/              # OPDS 2.0 models
│   ├── __init__.py
│   ├── base.py          # Base types (Link, Metadata)
│   ├── publication.py   # Publication models
│   ├── feed.py          # Feed/Collection models
│   └── acquisition.py   # Acquisition models
└── opds12/              # OPDS 1.2 specific module
    ├── __init__.py
    ├── client.py        # OPDS 1.2 Client
    ├── parser.py        # Atom/XML parsing (OPDS 1.2)
    ├── models.py        # OPDS 1.2 models
    ├── namespace.py     # XML namespace constants
    └── exceptions.py    # OPDS 1.2 exceptions

tests/
├── conftest.py
├── models/                # OPDS 2.0 model tests (mirrors opds_client/models/)
│   ├── __init__.py
│   ├── test_base.py       # Base types (Link, Metadata)
│   ├── test_publication.py  # Publication models
│   └── test_feed.py       # Feed/Collection models
├── opds12/                # OPDS 1.2 tests (mirrors opds_client/opds12/)
│   ├── __init__.py
│   ├── test_models.py     # OPDS 1.2 models
│   ├── test_parser.py     # Atom/XML parsing
│   ├── test_client.py     # OPDS 1.2 Client
│   └── fixtures/          # OPDS 1.2 XML fixtures
│       ├── root.xml
│       ├── acquisition.xml
│       └── facets.xml
├── test_parser.py         # OPDS 2.0 parser tests
├── test_client.py         # OPDS 2.0 client tests
├── test_acquisition.py    # Acquisition tests
├── test_exceptions.py     # Exception tests
├── test_integration.py    # Integration tests
├── test_utils.py          # Utility tests
└── fixtures/              # Test fixtures (JSON & XML)
    ├── opds12/            # OPDS 1.2 XML fixtures
    │   ├── root.xml
    │   ├── acquisition.xml
    │   └── facets.xml
    ├── feed.json
    ├── publication.json
    ├── facets.json
    └── groups.json
```

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MIT License - see [LICENSE](LICENSE) file for details.

## References

- [PyPI: opds-client](https://pypi.org/project/opds-client)
- [OPDS 2.0 Specification](https://specs.opds.io/opds-2.0)
- [OPDS 1.2 Specification](https://specs.opds.io/opds-1.2)
- [GitHub: sevdani/opds-client](https://github.com/sevdani/opds-client)
