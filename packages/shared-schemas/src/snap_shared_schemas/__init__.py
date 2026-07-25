"""Shared schemas and enums — the single source of truth for API contracts.

Enums and the error envelope land here (T-004). Endpoint payload models are added by
their owning tasks. TypeScript types are generated from the API's OpenAPI schema
(T-005), so clients never re-declare these values.
"""

from snap_shared_schemas.enums import (
    SEVERITY_BY_STATUS,
    SEVERITY_DISPLAY_ORDER,
    AllergenStatusCode,
    DataSourceKind,
    ErrorCode,
    EvidenceSource,
    InfoType,
    ScanMode,
    ScanState,
    Severity,
)
from snap_shared_schemas.errors import ErrorDetail, ErrorEnvelope

__version__ = "0.0.0"

__all__ = [
    "SEVERITY_BY_STATUS",
    "SEVERITY_DISPLAY_ORDER",
    "AllergenStatusCode",
    "DataSourceKind",
    "ErrorCode",
    "ErrorDetail",
    "ErrorEnvelope",
    "EvidenceSource",
    "InfoType",
    "ScanMode",
    "ScanState",
    "Severity",
    "__version__",
]
