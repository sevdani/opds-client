# Usage Examples

This page contains practical examples of using the OPDS Client library.

## Search Catalogs

### OPDS 2.0

```python
from opds_client import OPDSClient

client = OPDSClient()
feed = client.fetch_feed("https://example.com/opds")

# Check if search is supported
search_link = feed.get_search_link()
if search_link:
    results = client.search(feed, "science fiction")
    for pub in results.publications or []:
        print(f"- {pub.metadata.title}")
```

### OPDS 1.2

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")

# Check if search is supported
if feed.get_opensearch_link():
    # OPDS 1.2 uses OpenSearch for search
    pass
```

## Browse by Category

### OPDS 2.0

```python
from opds_client import OPDSClient

client = OPDSClient()
feed = client.fetch_feed("https://example.com/opds")

# Follow a category facet
category_feed = client.follow_facet(feed, "Category", "Science Fiction")

# Navigate to sub-category
sub_cat_feed = client.follow_facet(category_feed, "Subcategory", "Space Opera")
```

### OPDS 1.2

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")

# Get facet groups
for group in feed.facets or []:
    print(f"Facet Group: {group.title}")
    for link in group.links or []:
        print(f"  - {link.title} ({link.total_results or 0} items)")
```

## Acquisition

### OPDS 2.0

```python
from opds_client import OPDSClient
from opds_client.models import AcquisitionManager

client = OPDSClient()
pub = client.fetch_publication("https://example.com/publication")

# Get acquisition links
acq_links = pub.get_acquisition_links()

# Use acquisition manager
manager = AcquisitionManager(acq_links[0])

# Check for open access
if manager.get_open_access_link():
    # Download directly
    download_link = manager.get_open_access_link()
    print(f"Download: {download_link.href}")

# Check for buy link
buy_link = manager.get_buy_link()
if buy_link:
    price = buy_link.get_price()
    print(f"Price: {price.currency} {price.value}")
```

### OPDS 1.2

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")

# Get acquisition links from entries
entry = feed.entries[0]
acq_links = entry.get_acquisition_links()

# Check acquisition types
for link in acq_links:
    if "buy" in link.rel:
        print(f"Buy: {link.href}")
        price = link.get_price()
        if price:
            print(f"  Price: {price.currencycode} {price.value}")
    elif "borrow" in link.rel:
        print(f"Borrow: {link.href}")
```

## Pagination

### OPDS 2.0

```python
from opds_client import OPDSClient

client = OPDSClient()
feed = client.fetch_feed("https://example.com/opds?page=1")

# Paginate through results
current_feed = feed
while current_feed:
    for pub in current_feed.publications or []:
        print(f"- {pub.metadata.title}")
    
    # Get next page
    next_feed = client.get_next_page(current_feed)
    if next_feed:
        print(f"Next page: {next_feed.metadata.title}")
        current_feed = next_feed
    else:
        current_feed = None
```

### OPDS 1.2

```python
from opds_client import OPDS12Client

client = OPDS12Client()
feed = client.fetch_feed("https://example.com/opds.xml")

# Paginate through results
current_feed = feed
while current_feed:
    for entry in current_feed.entries or []:
        print(f"- {entry.title}")
    
    # Get next page
    next_feed = client.get_next_page(current_feed)
    if next_feed:
        current_feed = next_feed
    else:
        current_feed = None
```

## Error Handling

```python
from opds_client import (
    OPDSClient,
    OPDSHTTPError,
    OPDSParseError,
    OPDSNavigationError,
    SearchError,
)

client = OPDSClient()

try:
    feed = client.fetch_feed("https://example.com/opds")
    results = client.search(feed, "query")
except OPDSHTTPError as e:
    print(f"HTTP Error {e.status_code}: {e}")
except OPDSParseError as e:
    print(f"Parse Error: {e}")
except OPDSNavigationError as e:
    print(f"Navigation Error: {e}")
except SearchError as e:
    print(f"Search Error: {e}")
```
