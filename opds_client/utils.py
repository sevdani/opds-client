"""Utility functions for OPDS client."""

from __future__ import annotations

import re
from typing import Any, Optional


def merge_urls(base_url: str, relative_url: str) -> str:
    """Merge a base URL with a relative URL.

    Args:
        base_url: Base URL.
        relative_url: Relative URL or absolute URL.

    Returns:
        Merged absolute URL.
    """
    if relative_url.startswith(("http://", "https://")):
        return relative_url

    from urllib.parse import urljoin
    return urljoin(base_url, relative_url)


def extract_uri_template_params(template: str) -> list[str]:
    """Extract parameter names from URI template.

    Args:
        template: URI template string.

    Returns:
        List of parameter names.
    """
    import re
    matches = re.findall(r"\{([^}]+)\}", template)
    params = []
    for match in matches:
        if match.startswith("?"):
            match = match[1:]
        params.extend(match.split(","))
    return params


def is_uri_template(url: str) -> bool:
    """Check if URL is a URI template.

    Args:
        url: URL string.

    Returns:
        True if URL contains URI template parameters.
    """
    return bool(re.search(r"\{[^}]+\}", url))


def get_media_type_from_url(url: str) -> Optional[str]:
    """Extract media type from URL extension.

    Args:
        url: URL string.

    Returns:
        Media type string or None if not determinable.
    """
    extensions_map = {
        ".json": "application/json",
        ".opds": "application/opds+json",
        ".epub": "application/epub+zip",
        ".pdf": "application/pdf",
        ".mobi": "application/x-mobipocket-ebook",
        ".azw": "application/vnd.amazon.ebook",
        ".html": "text/html",
        ".xml": "application/xml",
    }

    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.lower()

    for ext, media_type in extensions_map.items():
        if path.endswith(ext):
            return media_type

    return None


def is_opds_feed_type(media_type: Optional[str]) -> bool:
    """Check if media type indicates OPDS feed.

    Args:
        media_type: Media type string.

    Returns:
        True if media type is OPDS.
    """
    if media_type is None:
        return False

    opds_types = [
        "application/opds+json",
        "application/opds-publication+json",
    ]

    return media_type in opds_types


def clean_blank_values(data: dict[str, Any]) -> dict[str, Any]:
    """Remove blank values from dictionary.

    Args:
        data: Dictionary to clean.

    Returns:
        Dictionary with blank values removed.
    """
    blank_values = [None, "", [], {}]

    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            cleaned = clean_blank_values(value)
            if cleaned:
                result[key] = cleaned
        elif isinstance(value, list):
            cleaned = [clean_blank_values(v) if isinstance(v, dict) else v for v in value]
            cleaned = [v for v in cleaned if v not in blank_values]
            if cleaned:
                result[key] = cleaned
        elif value not in blank_values:
            result[key] = value

    return result


def validate_identifier(identifier: str) -> bool:
    """Validate identifier format.

    Args:
        identifier: Identifier string.

    Returns:
        True if identifier is valid.
    """
    if not identifier:
        return False

    prefixes = [
        "urn:isbn:",
        "urn:issn:",
        "http://",
        "https://",
        "doi:",
    ]

    return any(identifier.startswith(prefix) for prefix in prefixes)


def parse_datetime(value: str) -> Optional[str]:
    """Parse datetime string to ISO format.

    Args:
        value: Datetime string.

    Returns:
        ISO format datetime string or None if invalid.
    """
    if not value:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    from datetime import datetime
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    return None
