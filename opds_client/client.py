"""OPDS 2.0 client."""

from __future__ import annotations

from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.auth import HTTPBasicAuth

from opds_client.exceptions import (
    OPDSHTTPError,
    OPDSNavigationError,
    OPDSParseError,
    OPDSValidationError,
    SearchError,
)
from opds_client.models import Link, OPDSFeed, OPDSPublication
from opds_client.parser import OPDSParser, URITemplateResolver
from opds_client.utils import merge_urls


class OPDSClient:
    """Client for OPDS 2.0 catalogs."""

    DEFAULT_HEADERS = {
        "Accept": "application/opds+json, application/json, */*",
        "User-Agent": "OPDS-Client/1.0",
    }

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        auth: requests.auth.AuthBase | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        session: requests.Session | None = None,
        parser: OPDSParser | None = None,
        origin: str | None = None,
    ):
        """Initialize OPDS client.

        Args:
            username: Username for HTTP Basic Auth.
            password: Password for HTTP Basic Auth.
            auth: Custom auth object (overrides username/password).
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries on error.
            backoff_factor: Backoff factor for retries.
            session: Optional requests session to reuse.
            parser: Optional OPDS parser instance.
            origin: Optional base URL to prepend to relative URLs.
        """
        self.timeout = timeout
        self.session = session or requests.Session()
        self.origin = origin

        # Configure authentication
        if auth is not None:
            self.session.auth = auth
        elif username is not None and password is not None:
            self.session.auth = HTTPBasicAuth(username, password)

        if max_retries > 0:
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

        self.parser = parser or OPDSParser()

    def _prepare_url(self, url: str) -> str:
        """Prepare URL by merging with origin if needed.

        Args:
            url: URL string.

        Returns:
            Merged absolute URL.
        """
        if self.origin is not None:
            return merge_urls(self.origin, url)
        return url

    def fetch_feed(self, url: str) -> "OPDSFeed":
        """Fetch and parse an OPDS feed.

        Args:
            url: URL of the OPDS feed.

        Returns:
            Parsed OPDSFeed object.

        Raises:
            OPDSHTTPError: If HTTP request fails.
            OPDSParseError: If parsing fails.
            OPDSValidationError: If validation fails.
            OPDSNavigationError: If navigation fails.
        """
        try:
            response = self.session.get(
                self._prepare_url(url),
                headers=self.DEFAULT_HEADERS,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                raise OPDSHTTPError(
                    f"HTTP error {e.response.status_code}",
                    e.response.status_code,
                    self._prepare_url(url),
                    e.response.text,
                ) from e
            raise OPDSHTTPError(str(e), 0, self._prepare_url(url)) from e

        try:
            feed = self.parser.parse(response.text)
            feed._url = url
            return feed
        except (OPDSParseError, OPDSValidationError) as e:
            raise e

    def fetch_publication(self, url: str) -> "OPDSPublication":
        """Fetch and parse an OPDS publication.

        Args:
            url: URL of the OPDS publication.

        Returns:
            Parsed OPDSPublication object.

        Raises:
            OPDSHTTPError: If HTTP request fails.
            OPDSParseError: If parsing fails.
            OPDSValidationError: If validation fails.
        """
        headers = self.DEFAULT_HEADERS.copy()
        headers["Accept"] = (
            "application/opds-publication+json, application/opds+json, application/json, */*"
        )

        try:
            response = self.session.get(self._prepare_url(url), headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                raise OPDSHTTPError(
                    f"HTTP error {e.response.status_code}",
                    e.response.status_code,
                    self._prepare_url(url),
                    e.response.text,
                ) from e
            raise OPDSHTTPError(str(e), 0, self._prepare_url(url)) from e

        try:
            publication = self.parser.parse_publication(response.text)
            publication._url = self._prepare_url(url)
            return publication
        except (OPDSParseError, OPDSValidationError) as e:
            raise e

    def follow_link(self, link: "Link", **params: str | int | float) -> "OPDSFeed":
        """Follow a link and fetch the target feed.

        Args:
            link: Link object to follow.
            **params: Parameters for URI template resolution.

        Returns:
            Parsed OPDSFeed object.

        Raises:
            OPDSNavigationError: If link cannot be followed.
            OPDSHTTPError: If HTTP request fails.
        """
        if link.templated:
            url = URITemplateResolver.fill_template(str(link.href), **params)
        else:
            url = str(link.href)

        return self.fetch_feed(self._prepare_url(url))

    def navigate_to(self, feed: "OPDSFeed", rel: str, **params: str | int | float) -> "OPDSFeed":
        """Navigate to a feed using a link relation.

        Args:
            feed: Current OPDS feed.
            rel: Link relation to follow.
            **params: Parameters for URI template resolution.

        Returns:
            Parsed OPDSFeed object.

        Raises:
            OPDSNavigationError: If link with relation not found.
        """
        link = feed.get_link_by_rel(rel)
        if link is None:
            raise OPDSNavigationError(f"Link with relation '{rel}' not found")

        return self.follow_link(link, **params)

    def get_link_by_rel(self, feed: "OPDSFeed", rel: str) -> Optional["Link"]:
        """Get a link by relation from feed.

        Args:
            feed: OPDS feed.
            rel: Link relation to find.

        Returns:
            Link object or None if not found.
        """
        return feed.get_link_by_rel(rel)

    def search(
        self,
        feed: "OPDSFeed",
        query: str,
        **filters: str | int | float,
    ) -> "OPDSFeed":
        """Search an OPDS feed.

        Args:
            feed: OPDS feed with search link.
            query: Search query string.
            **filters: Additional filter parameters.

        Returns:
            Parsed OPDSFeed object with search results.

        Raises:
            SearchError: If search is not supported.
            OPDSHTTPError: If HTTP request fails.
            OPDSNavigationError: If navigation fails.
        """
        search_link = feed.get_search_link()
        if search_link is None:
            raise SearchError("Search is not supported by this catalog")

        params = {"query": query}
        params.update(filters)

        try:
            return self.follow_link(search_link, **params)
        except OPDSHTTPError as e:
            raise SearchError(f"Search failed: {e}") from e

    def get_next_page(self, feed: "OPDSFeed") -> Optional["OPDSFeed"]:
        """Get the next page of results.

        Args:
            feed: Current OPDS feed.

        Returns:
            Next page OPDSFeed or None if no next page.
        """
        next_link = feed.get_next_link()
        if next_link is None:
            return None

        return self.follow_link(next_link)

    def get_previous_page(self, feed: "OPDSFeed") -> Optional["OPDSFeed"]:
        """Get the previous page of results.

        Args:
            feed: Current OPDS feed.

        Returns:
            Previous page OPDSFeed or None if no previous page.
        """
        prev_link = feed.get_previous_link()
        if prev_link is None:
            return None

        return self.follow_link(prev_link)

    def get_first_page(self, feed: "OPDSFeed") -> Optional["OPDSFeed"]:
        """Get the first page of results.

        Args:
            feed: Current OPDS feed.

        Returns:
            First page OPDSFeed or None if already on first page.
        """
        first_link = feed.get_first_link()
        if first_link is None:
            return None

        return self.follow_link(first_link)

    def get_last_page(self, feed: "OPDSFeed") -> Optional["OPDSFeed"]:
        """Get the last page of results.

        Args:
            feed: Current OPDS feed.

        Returns:
            Last page OPDSFeed or None if already on last page.
        """
        last_link = feed.get_last_link()
        if last_link is None:
            return None

        return self.follow_link(last_link)

    def follow_navigation(self, feed: "OPDSFeed", title: str) -> "OPDSFeed":
        """Follow a navigation link by title.

        Args:
            feed: OPDS feed with navigation.
            title: Title of navigation link to follow.

        Returns:
            Parsed OPDSFeed object.

        Raises:
            OPDSNavigationError: If navigation link not found.
        """
        if feed.navigation is None:
            raise OPDSNavigationError("Feed has no navigation links")

        for nav_link in feed.navigation:
            if nav_link.title == title:
                return self.follow_link(nav_link)

        raise OPDSNavigationError(f"Navigation link with title '{title}' not found")

    def follow_facet(self, feed: "OPDSFeed", facet_title: str, link_title: str) -> "OPDSFeed":
        """Follow a facet link by facet and link title.

        Args:
            feed: OPDS feed with facets.
            facet_title: Title of the facet group.
            link_title: Title of the facet link to follow.

        Returns:
            Parsed OPDSFeed object.

        Raises:
            OPDSNavigationError: If facet or link not found.
        """
        facet = feed.get_facets_by_title(facet_title)
        if facet is None:
            raise OPDSNavigationError(f"Facet '{facet_title}' not found")

        link = facet.get_facet_by_title(link_title)
        if link is None:
            raise OPDSNavigationError(f"Facet link '{link_title}' not found")

        return self.follow_link(link)

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> "OPDSClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
