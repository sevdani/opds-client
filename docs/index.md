# Welcome to OPDS Client

A Python library for working with OPDS catalogs, supporting both [OPDS 1.2](https://specs.opds.io/opds-1.2) (Atom/XML) and [OPDS 2.0](https://specs.opds.io/opds-2.0) (JSON) specifications.

## Features

### OPDS 2.0 (JSON)
- Parse OPDS 2.0 feeds and publications
- Validate against OPDS 2.0 specification
- Navigate navigation, publications, groups, and facets collections
- Handle pagination (first, previous, next, last links)
- Search catalogs with URI template resolution
- Work with acquisition links (download, buy, borrow, etc.)
- HTTP error handling with retries
- Pydantic models for type safety

### OPDS 1.2 (Atom/XML)
- Parse OPDS 1.2 Atom feeds and entries
- Dublin Core metadata support
- Navigation and Acquisition feeds
- Facet groups with active facets and item counts
- Acquisition links with prices and indirect acquisitions
- OpenSearch integration
- Multiple acquisition relations (buy, borrow, subscribe, etc.)

## Documentation

- [Getting Started](getting-started.md)
- [OPDS 2.0 Guide](opds2.md)
- [OPDS 1.2 Guide](opds12.md)
- [API Reference](api.md)

## License

MIT License - see the [LICENSE](../LICENSE) file in the repository for details.
