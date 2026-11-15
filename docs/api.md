# API Reference

## OPDS 2.0 API

### Client

::: opds_client.OPDSClient

### Models

::: opds_client.models.Link

::: opds_client.models.AcquisitionLink

::: opds_client.models.NavigationLink

::: opds_client.models.Metadata

::: opds_client.models.OPDSPublication

::: opds_client.models.OPDSFeed

::: opds_client.models.Facet

::: opds_client.models.Group

### Acquisition

::: opds_client.models.AcquisitionManager

### Exceptions

::: opds_client.exceptions.OPDSHTTPError

::: opds_client.exceptions.OPDSParseError

::: opds_client.exceptions.OPDSValidationError

::: opds_client.exceptions.OPDSNavigationError

::: opds_client.exceptions.SearchError

## OPDS 1.2 API

### Client

::: opds_client.opds12.OPDS12Client

### Models

::: opds_client.opds12.models.Link

::: opds_client.opds12.models.Entry

::: opds_client.opds12.models.Feed

::: opds_client.opds12.models.FacetGroup

### Parser

::: opds_client.opds12.OPDS12Parser

### Exceptions

OPDS 1.2 uses the same exceptions as OPDS 2.0:

- `OPDSHTTPError`
- `OPDSParseError`
- `OPDSValidationError`
- `OPDSNavigationError`
