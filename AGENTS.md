# AGENTS.md

This file provides guidance for AI agents (and developers) working with the OPDS Client codebase.

## Project Overview

The OPDS Client is a Python library for working with OPDS (Open Publication Distribution System) catalogs. It supports both:

- **OPDS 1.2** (Atom/XML format)
- **OPDS 2.0** (JSON format)

The library provides parsing, navigation, authentication, and acquisition functionality for digital publication catalogs.

## Naming Conventions

- **OPDS 2.0 classes**: No version suffix (e.g., `OPDSClient`, `OPDSFeed`, `OPDSPublication`)
- **OPDS 1.2 classes**: Prefixed with `OPDS12` (e.g., `OPDS12Client`, `OPDS12Feed`, `OPDS12Entry`)

## How to Work with the Codebase

### Adding a New Feature

1. **Determine which version(s)** need the feature
2. **OPDS 2.0**: Add to appropriate model or client method
3. **OPDS 1.2**: Add to `opds12/` module
4. **Both versions**: Ensure consistent API across both

### Modifying Parsing Logic

- **OPDS 2.0**: Modify `opds_client/parser.py`
- **OPDS 1.2**: Modify `opds_client/opds12/parser.py`
- Both use Pydantic models for validation

### Adding Tests

Test structure mirrors the source:

```
tests/
├── test_*.py           # OPDS 2.0 tests
├── opds12/             # OPDS 1.2 tests
│   ├── test_*.py
│   └── fixtures/       # XML test fixtures
└── fixtures/           # JSON test fixtures
```

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
pytest tests/test_client.py
```

## Linting and Formatting

```bash
# Run linter (checks for E, F, W, I rules)
ruff check .

# Fix linting issues automatically
ruff check . --fix
```
