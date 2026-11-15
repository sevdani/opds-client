# AGENTS.md

This file provides guidance for AI agents (and developers) working with the OPDS Client codebase.

## Project Overview

The OPDS Client is a Python library for working with OPDS (Open Publication Distribution System) catalogs. It supports both:

- **OPDS 1.2** (Atom/XML format)
- **OPDS 2.0** (JSON format)

The library provides parsing, navigation, authentication, and acquisition functionality for digital publication catalogs.

## Naming Conventions

- **OPDS 2.0 classes**: Prefixed with `OPDS2` (e.g., `OPDS2Client`, `OPDS2Parser`, `OPDSFeed`, `OPDSPublication`)
- **OPDS 1.2 classes**: Prefixed with `OPDS12` (e.g., `OPDS12Client`, `OPDS12Parser`, `OPDS12Feed`, `OPDS12Entry`)

### Module Structure and API

The library exposes modules in multiple ways for convenience:

- **OPDS 2.0**: Access via `opds_client.opds2`, `opds_client.v2_0`, or top-level `OPDS2*` classes
- **OPDS 1.2**: Access via `opds_client.opds12`, `opds_client.v1_2`, or top-level `OPDS12*` classes

## How to Work with the Codebase

### Adding a New Feature

1. **Determine which version(s)** need the feature
2. **OPDS 2.0**: Add to appropriate model or client method in `opds2/` module
3. **OPDS 1.2**: Add to appropriate model or client method in `opds12/` module
4. **Both versions**: Ensure consistent API across both

### Modifying Parsing Logic

- **OPDS 2.0**: Modify `opds_client/opds2/parser.py`
- **OPDS 1.2**: Modify `opds_client/opds12/parser.py`
- Both use Pydantic models for validation

### Adding Tests

Tests follow the same structure as the source code:

- **OPDS 2.0 tests**: Add to `tests/opds2/`
- **OPDS 1.2 tests**: Add to `tests/opds12/`

## Development Guidelines

1. **Type hints**: Use Python type hints (the project uses mypy with strict mode)
2. **Docstrings**: Follow the existing docstring format
3. **Error handling**: Use custom exceptions from `opds_client.exceptions`
4. **Consistency**: Maintain API consistency between OPDS 1.2 and 2.0 where appropriate
5. **Tests**: Add tests for new functionality

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=opds_client

# Type checking
mypy opds_client

# Run specific test file
pytest tests/opds2/test_client.py
```

## Linting and Formatting

```bash
# Run linter (checks for E, F, W, I rules)
ruff check .

# Fix linting issues automatically
ruff check . --fix
```
