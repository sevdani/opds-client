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

[Features](#features) · [Installation](#installation) · [Quick Start](#quick-start) · [Authentication](#authentication) · [Models](#models) · [Usage Examples](#usage-examples) · [OPDS 1.2 vs OPDS 2.0](#opds-12-vs-opds-20) · [Testing](#testing) · [Documentation](#documentation) · [Project Structure](#project-structure) · [License](#license)

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
from opds_client import OPDS2Client

# Create a client
client = OPDS2Client()

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
```

## Documentation

The full documentation is available at: **https://sevdani.github.io/opds-client**

The documentation is built with [Zensical](https://zensical.org/) (successor to Material for MkDocs).

### Building Documentation Locally

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build with Zensical
zensical build

# Build with MkDocs (legacy)
mkdocs build

# Preview with Zensical
zensical serve

# Preview with MkDocs (legacy)
mkdocs serve
```

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MIT License - see [LICENSE](LICENSE) file for details.

## References

- [PyPI: opds-client](https://pypi.org/project/opds-client)
- [OPDS 2.0 Specification](https://specs.opds.io/opds-2.0)
- [OPDS 1.2 Specification](https://specs.opds.io/opds-1.2)
- [GitHub: sevdani/opds-client](https://github.com/sevdani/opds-client)
