# Development

This guide covers development and contribution to the OPDS Client library.

## Project Structure

```
opds_client/
├── __init__.py          # Package exports (OPDS 1.2 & 2.0)
├── utils.py             # Utility functions
├── opds2/               # OPDS 2.0 specific module
│   ├── __init__.py      # Module exports
│   ├── client.py        # OPDS 2.0 Client
│   ├── parser.py        # JSON parsing/validation (OPDS 2.0)
│   ├── models/          # OPDS 2.0 models
│   │   ├── __init__.py
│   │   ├── base.py      # Base types (Link, Metadata)
│   │   ├── publication.py   # Publication models
│   │   ├── feed.py          # Feed/Collection models
│   │   └── acquisition.py   # Acquisition models
│   └── exceptions.py    # OPDS 2.0 exceptions
└── opds12/              # OPDS 1.2 specific module
    ├── __init__.py      # Module exports
    ├── client.py        # OPDS 1.2 Client
    ├── parser.py        # Atom/XML parsing (OPDS 1.2)
    ├── models.py        # OPDS 1.2 models
    ├── namespace.py     # XML namespace constants
    └── exceptions.py    # OPDS 1.2 exceptions

tests/
├── conftest.py          # Test fixtures
├── opds2/               # OPDS 2.0 tests
│   ├── test_*.py
│   └── models/          # Model tests
└── opds12/              # OPDS 1.2 tests
    ├── test_*.py
    └── fixtures/        # XML test fixtures
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
pytest tests/opds2/test_client.py
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
zensical build

# Serve documentation locally
zensical serve
```
