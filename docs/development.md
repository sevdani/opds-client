# Development

This guide covers development and contribution to the OPDS Client library.

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
├── test_*.py            # OPDS 2.0 tests
├── opds12/              # OPDS 1.2 tests
│   ├── test_*.py
│   └── fixtures/        # XML test fixtures
└── fixtures/            # JSON test fixtures
```

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=opds_client

# Run specific test file
pytest tests/test_client.py
```

## Type Checking

```bash
# Run mypy type checker
mypy opds_client
```

## Code Quality

```bash
# Run ruff linter
ruff check .

# Fix linting issues
ruff check . --fix

# Format code
ruff format .
```

## Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```
