"""Canonical enumerations — the single source of truth for these vocabularies.

Every value here is normative and traced to a design doc. Changing an allergen
status code or severity is a **safety change** (requires review + an ALLERGEN_POLICY
changelog entry). Other surfaces (API, mobile, DB) must import these rather than
re-declaring string literals.

Convention: allergen status codes use the exact UPPERCASE tokens from
docs/safety/ALLERGEN_POLICY.md (they are the normative "stable API values"). Other
enums use lowercase snake_case values matching their source docs.
"""

from enum import StrEnum


class InfoType(StrEnum):
    """The 7-way typed-information taxonomy (docs/product/PRODUCT_VISION.md §1).

    Every displayed fact is exactly one of these; the UI never blends them.
    """

    OBSERVED = "observed"  # OCR / barcode read
    RETRIEVED = "retrieved"  # authoritative record (USDA/OFF)
    PREDICTED = "predicted"  # model output
    USER_PROVIDED = "user_provided"
    ESTIMATED = "estimated"  # derived with assumptions (e.g., serving math)
    MISSING = "missing"  # missing or uncertain
    WARNING = "warning"  # safety warning


class Severity(StrEnum):
    """Evidence-severity display taxonomy (docs/safety/SAFETY_MODEL.md).

    Grades *evidence*, not medical risk. Not collected from users.
    """

    S0 = "S0"  # no terms found in readable text — neutral, never "safe"/green
    S1 = "S1"  # declared conflict
    S2 = "S2"  # trace / facility conflict
    S3 = "S3"  # derived / synonym match
    S4 = "S4"  # inferred possibility (class hint; unverifiable)
    S5 = "S5"  # unknown / insufficient / unreadable


class AllergenStatusCode(StrEnum):
    """Closed set of per-(scan x profile-allergen) statuses (docs/safety/ALLERGEN_POLICY.md).

    Order of declaration is documentation order, NOT display order — use
    SEVERITY_DISPLAY_ORDER for sorting.
    """

    DECLARED = "DECLARED"
    MAY_CONTAIN = "MAY_CONTAIN"
    FACILITY = "FACILITY"
    SYNONYM = "SYNONYM"
    POSSIBLE_SYNONYM = "POSSIBLE_SYNONYM"
    CLASS_RISK = "CLASS_RISK"
    NOT_FOUND = "NOT_FOUND"
    INSUFFICIENT = "INSUFFICIENT"
    OCR_UNCERTAIN = "OCR_UNCERTAIN"
    USER_CONFIRM_REQUIRED = "USER_CONFIRM_REQUIRED"


# Severity for each evidence-bearing status (ALLERGEN_POLICY headers).
# USER_CONFIRM_REQUIRED is a pre-evidence gate, not an evidence severity, so it is
# deliberately excluded from this mapping.
SEVERITY_BY_STATUS: dict[AllergenStatusCode, Severity] = {
    AllergenStatusCode.DECLARED: Severity.S1,
    AllergenStatusCode.MAY_CONTAIN: Severity.S2,
    AllergenStatusCode.FACILITY: Severity.S2,
    AllergenStatusCode.SYNONYM: Severity.S3,
    AllergenStatusCode.POSSIBLE_SYNONYM: Severity.S3,
    AllergenStatusCode.CLASS_RISK: Severity.S4,
    AllergenStatusCode.NOT_FOUND: Severity.S0,
    AllergenStatusCode.INSUFFICIENT: Severity.S5,
    AllergenStatusCode.OCR_UNCERTAIN: Severity.S5,
}

# Display ordering: positive findings first, negatives last (ALLERGEN_POLICY
# "Ordering & prominence rules": S1 -> S2 -> S3 -> S4 -> S5 -> S0).
SEVERITY_DISPLAY_ORDER: tuple[Severity, ...] = (
    Severity.S1,
    Severity.S2,
    Severity.S3,
    Severity.S4,
    Severity.S5,
    Severity.S0,
)


class ScanMode(StrEnum):
    """Scan capture modes (docs/architecture/API_DESIGN.md POST /v1/scans)."""

    PHOTO = "photo"
    LABEL = "label"
    PANEL = "panel"
    BARCODE = "barcode"


class ScanState(StrEnum):
    """Scan lifecycle states (docs/architecture/BACKEND_ARCHITECTURE.md state machine).

    The exact transition table is implemented in T-017; new members may be added
    there without breaking this vocabulary.
    """

    CREATED = "created"
    UPLOADED = "uploaded"
    QUALITY_CHECKED = "quality_checked"
    CLASSIFYING = "classifying"
    OCR_RUNNING = "ocr_running"
    BARCODE_LOOKUP = "barcode_lookup"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    ENRICHING = "enriching"
    ENRICHED = "enriched"
    ENRICHMENT_PARTIAL = "enrichment_partial"
    COMPLETE = "complete"
    # Failure branches (retryable; see docs/reliability/FAILURE_HANDLING.md).
    UPLOAD_FAILED = "upload_failed"
    CLASSIFICATION_FAILED = "classification_failed"
    OCR_FAILED = "ocr_failed"
    FAILED = "failed"


class EvidenceSource(StrEnum):
    """Origin of an allergen-evidence row (docs/architecture/DATA_MODEL.md)."""

    OCR = "ocr"
    OFF = "off"  # Open Food Facts tags
    CLASS_HINT = "class_hint"  # inferred from confirmed food class


class DataSourceKind(StrEnum):
    """Provenance kind for nutrition/product records (docs/architecture/DATA_MODEL.md)."""

    FDC = "fdc"  # USDA FoodData Central
    OFF = "off"  # Open Food Facts
    USER_OCR = "user_ocr"  # user-confirmed OCR panel
    CURATED = "curated"  # curated internal mapping


class ErrorCode(StrEnum):
    """Canonical API error codes (docs/architecture/API_DESIGN.md)."""

    VALIDATION_ERROR = "validation_error"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMITED = "rate_limited"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROCESSING_FAILED = "processing_failed"
    QUOTA_DEGRADED = "quota_degraded"
