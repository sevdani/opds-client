# Makefile for opds-client

.PHONY: test test-cov lint typecheck build publish release

# Default target
all: test lint typecheck

# Run tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest -v --cov=opds_client --cov-report=term-missing

# Run linter
lint:
	ruff check .

# Run type checker
typecheck:
	mypy opds_client

# Build package
build:
	python -m build --sdist --wheel .

# Install dev dependencies
install-dev:
	pip install -e ".[dev]"

# Install release dependencies
install-release:
	pip install -e ".[release]"

# Run semantic-release version (determines version bump)
# Usage: make release-version level=patch
release-version:
	bump2version $(level)

# Run semantic-release build (builds package)
# Usage: make release-build level=minor
release-build:
	bump2version $(level)

# Run semantic-release publish (creates tag + release + upload)
# Usage: make release-publish level=major
release-publish:
	bump2version $(level)
	git push origin main --tags

# Full release process (determines version, builds, publishes)
# Usage: make release level=patch
release: install-release
	bump2version $(level)
	git push origin main --tags
	@echo "Release prepared. Version bumped to: $(level)"

# Tag and release manually (after version bump)
# Usage: make tag-release
tag-release:
	bump2version patch
	git push origin main --tags

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Update dependencies
update-deps:
	pip install --upgrade pip
	pip install -e ".[dev]"
	pip install -e ".[release]"
