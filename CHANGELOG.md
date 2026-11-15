# Changelog for opds-client

## [Unreleased]

## [1.1.0] - 2026-11-15

### Added
- Dedicated exception classes for OPDS 2.0 (`opds_client.opds2.exceptions`)
- Dedicated exception classes for OPDS 1.2 (`opds_client.opds12.exceptions`)
- New module structure with `opds_client/opds2/` and `opds_client/opds12/` packages
- Import aliases `v1_2` and `v2_0` for version-specific access
- `URITemplateResolver` class for resolving URI templates in OPDS 2.0
- Comprehensive documentation site (zensical) with:
  - API reference (`docs/api.md`)
  - Getting started guide (`docs/getting-started.md`)
  - OPDS 1.2 guide (`docs/opds12.md`)
  - OPDS 2.0 guide (`docs/opds2.md`)
  - Examples (`docs/examples.md`)
  - Development guide (`docs/development.md`)

### Changed
- **Major refactor**: Restructured codebase into separate `opds2/` and `opds12/` modules
- **API redesign**: Top-level imports reorganized to `OPDS2Client` and `OPDS12Client`
- Version-specific modules expose their own models, exceptions, and parsers
- Improved package structure for better organization and maintainability
- Updated `pyproject.toml` with new package configuration for modular structure
- Added separate dependency groups for docs and release management
- Enhanced type checking configuration with `strict_equality` and `extra_checks`

### Removed
- Legacy flat structure (`opds_client/models/`, single client)
- Old `OPDSClient` class (replaced by version-specific clients)

### Testing
- Tests reorganized to mirror new module structure (`tests/opds2/`, `tests/opds12/`)
- Updated fixtures for both OPDS 1.2 (XML) and OPDS 2.0 (JSON) formats
- Test coverage maintained for all OPDS 1.2 and OPDS 2.0 features

## [1.0.0] - 2026-11-14
Initial release with OPDS 1.2 and OPDS 2.0 support.

### Added
- OPDS 1.2 (Atom/XML) support
- OPDS 2.0 (JSON) support
- Pydantic models for type safety
- Full test coverage (185+ tests)
- Origin parameter support for base URL handling

### Changed
- Improved URL handling with origin parameter
- Refactored test folder structure to mirror source code

### Testing
- 185 tests passing
- Full test coverage for OPDS 1.2 and OPDS 2.0 features
