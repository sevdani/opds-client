"""OPDS 1.2 client."""

from __future__ import annotations

from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

from opds_client.exceptions import OPDSHTTPError
from opds_client.opds12.models import Entry, Feed, Link
from opds_client.opds12.parser import OPDS12Parser
from opds_client.utils import merge_urls


class OPDS12Client:
    """Client for OPDS 1.2 catalogs."""

    DEFAULT_HEADERS = {
        "Accept": "application/atom+xml, application/xml, */*",
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
        parser: OPDS12Parser | None = None,
        origin: str | None = None,
    ):
        """Initialize OPDS 1.2 client.

        Args:
            username: Username for HTTP Basic Auth.
            password: Password for HTTP Basic Auth.
            auth: Custom auth object (overrides username/password).
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries on error.
            backoff_factor: Backoff factor for retries.
            session: Optional requests session to reuse.
            parser: Optional OPDS 1.2 parser instance.
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
            from requests.adapters import HTTPAdapter, Retry

            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

        self.parser = parser or OPDS12Parser()

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

    def fetch_feed(self, url: str) -> Feed:
        """Fetch and parse an OPDS 1.2 feed.

        Args:
            url: URL of the OPDS feed.

        Returns:
            Parsed Feed object.

        Raises:
            OPDSHTTPError: If HTTP request fails.
            OPDSParseError: If parsing fails.
            OPDSValidationError: If validation fails.
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
            feed._url = self._prepare_url(url)  # type: ignore[attr-defined]
            return feed
        except Exception as e:
            raise e

    def fetch_entry(self, url: str) -> Entry:
        """Fetch and parse an OPDS 1.2 entry.

        Args:
            url: URL of the OPDS entry.

        Returns:
            Parsed Entry object.

        Raises:
            OPDSHTTPError: If HTTP request fails.
            OPDSParseError: If parsing fails.
            OPDSValidationError: If validation fails.
        """
        headers = self.DEFAULT_HEADERS.copy()
        headers["Accept"] = "application/atom+xml;type=entry;profile=opds-catalog"

        try:
            response = self.session.get(
                self._prepare_url(url), headers=headers, timeout=self.timeout
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
            entry = self.parser.parse_entry(response.text)
            entry._url = self._prepare_url(url)  # type: ignore[attr-defined]
            return entry
        except Exception as e:
            raise e

    def follow_link(self, link: Link, **params: str | int | float) -> Feed:
        """Follow a link and fetch the target feed.

        Args:
            link: Link object to follow.
            **params: Parameters for URI template resolution.

        Returns:
            Parsed Feed object.

        Raises:
            OPDSNavigationError: If link cannot be followed.
            OPDSHTTPError: If HTTP request fails.
        """
        url = str(link.href)

        return self.fetch_feed(self._prepare_url(url))

    def navigate_to(self, feed: Feed, rel: str) -> Optional[Feed]:
        """Navigate to a feed using a link relation.

        Args:
            feed: Current OPDS feed.
            rel: Link relation to follow.

        Returns:
            Parsed Feed object or None if not found.
        """
        link = self._get_link_by_rel(feed, rel)
        if link is None:
            return None

        return self.follow_link(link)

    def _get_link_by_rel(self, feed: Feed, rel: str) -> Optional[Link]:
        """Get a link by relation from feed.

        Args:
            feed: OPDS feed.
            rel: Link relation to find.

        Returns:
            Link object or None if not found.
        """
        if not feed.links:
            return None
        for link in feed.links:
            if link.rel == rel:
                return link
        return None

    def get_next_page(self, feed: Feed) -> Optional[Feed]:
        """Get the next page of results.

        Args:
            feed: Current OPDS feed.

        Returns:
            Next page Feed or None if no next page.
        """
        next_link = feed.get_next_link()
        if next_link is None:
            return None

        return self.follow_link(next_link)

    def get_previous_page(self, feed: Feed) -> Optional[Feed]:
        """Get the previous page of results.

        Args:
            feed: Current OPDS feed.

        Returns:
            Previous page Feed or None if no previous page.
        """
        prev_link = feed.get_previous_link()
        if prev_link is None:
            return None

        return self.follow_link(prev_link)

    def get_start_link(self, feed: Feed) -> Optional[Feed]:
        """Get the OPDS catalog root.

        Args:
            feed: Current OPDS feed.

        Returns:
            Root Feed or None if not available.
        """
        start_link = feed.get_start_link()
        if start_link is None:
            return None

        return self.follow_link(start_link)

    def get_crawlable_feed(self, feed: Feed) -> Optional[Feed]:
        """Get the complete acquisition feed for crawling.

        Args:
            feed: Current OPDS feed.

        Returns:
            Complete acquisition Feed or None if not available.
        """
        crawlable_link = feed.get_crawlable_link()
        if crawlable_link is None:
            return None

        return self.follow_link(crawlable_link)

    def follow_acquisition(
        self,
        entry: Entry,
        acquisition_type: str = "buy",
    ) -> Optional[Link]:
        """Follow an acquisition link from an entry.

        Args:
            entry: OPDS entry.
            acquisition_type: Type of acquisition (buy, borrow, etc.).

        Returns:
            Acquisition Link or None if not found.
        """
        acquisition_links = entry.get_acquisition_links()

        for link in acquisition_links:
            rel_value = link.rel
            if isinstance(rel_value, list):
                if acquisition_type in rel_value:
                    return link
            elif rel_value is not None:
                if acquisition_type in rel_value:
                    return link

        # Fallback to any acquisition link
        if acquisition_links:
            return acquisition_links[0]

        return None

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> "OPDS12Client":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Context manager exit."""
        self.close()
