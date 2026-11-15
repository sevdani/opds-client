# Getting Started

This guide will help you get started with the OPDS Client library.

## Installation

Install the package using pip:

```bash
pip install opds-client
```

For development installation with all dependencies:

```bash
pip install -e ".[dev,docs]"
```

## Basic Usage

### OPDS 2.0 Client

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

# Close the client
client.close()
```

### OPDS 1.2 Client

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

# Close the client
client.close()
```

## Working with Base URL

Both clients support setting a base URL (origin) for relative paths:

```python
from opds_client import OPDSClient

client = OPDSClient(origin="https://example.com")
feed = client.fetch_feed("/catalog")  # → https://example.com/catalog
```

## Authentication

### Basic Auth

```python
from opds_client import OPDSClient

client = OPDSClient(username="your_username", password="your_password")
feed = client.fetch_feed("https://example.com/opds")
```

### Custom Auth

```python
from opds_client import OPDSClient
from requests.auth import HTTPDigestAuth

client = OPDSClient(auth=HTTPDigestAuth("username", "password"))
feed = client.fetch_feed("https://example.com/opds")
```

## Error Handling

The library provides custom exceptions:

```python
from opds_client import OPDSClient, OPDSHTTPError, OPDSParseError

client = OPDSClient()
try:
    feed = client.fetch_feed("https://example.com/opds")
except OPDSHTTPError as e:
    print(f"HTTP Error: {e}")
except OPDSParseError as e:
    print(f"Parse Error: {e}")
```
