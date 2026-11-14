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
release-version:
	semantic-release version

# Run semantic-release build (builds package)
release-build:
	semantic-release build

# Run semantic-release publish (creates tag + release + upload)
release-publish:
	semantic-release publish

# Full release process (determines version, builds, publishes)
release: install-release
	semantic-release version --no-push --no-vcs-release
	semantic-release publish --no-push
	@echo "Release prepared locally. To push changes:"
	@echo "  git push origin main --tags"

# Tag and release manually (after version bump)
tag-release:
	git tag -a v$(shell grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2) -m "Release v$(shell grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)"
	git push origin --tags

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Update dependencies
update-deps:
	pip install --upgrade pip
	pip install -e ".[dev]"
	pip install -e ".[release]"
