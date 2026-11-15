# API Reference

## OPDS 2.0 API

### Client

::: opds_client.OPDS2Client

### Models

::: opds_client.opds2.models.Link

::: opds_client.opds2.models.AcquisitionLink

::: opds_client.opds2.models.NavigationLink

::: opds_client.opds2.models.Metadata

::: opds_client.opds2.models.OPDSPublication

::: opds_client.opds2.models.OPDSFeed

::: opds_client.opds2.models.Facet

::: opds_client.opds2.models.Group

### Acquisition

::: opds_client.opds2.models.AcquisitionManager

### Parser

::: opds_client.opds2.OPDS2Parser

::: opds_client.opds2.URITemplateResolver

### Exceptions

::: opds_client.opds2.exceptions.OPDSHTTPError

::: opds_client.opds2.exceptions.OPDSParseError

::: opds_client.opds2.exceptions.OPDSValidationError

::: opds_client.opds2.exceptions.OPDSNavigationError

::: opds_client.opds2.exceptions.SearchError

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
