"""Literal tests pinning enum values to the design docs.

These are intentionally hard-coded (not derived from the enums) so that an accidental
edit to a normative value fails loudly. Sources: docs/safety/ALLERGEN_POLICY.md,
docs/safety/SAFETY_MODEL.md, docs/architecture/API_DESIGN.md,
docs/architecture/DATA_MODEL.md, docs/product/PRODUCT_VISION.md.
"""

import pytest
from pydantic import ValidationError

from snap_shared_schemas import (
    SEVERITY_BY_STATUS,
    SEVERITY_DISPLAY_ORDER,
    AllergenStatusCode,
    DataSourceKind,
    ErrorCode,
    ErrorDetail,
    ErrorEnvelope,
    EvidenceSource,
    InfoType,
    ScanMode,
    ScanState,
    Severity,
)


def test_allergen_status_codes_exact_set() -> None:
    assert {s.value for s in AllergenStatusCode} == {
        "DECLARED",
        "MAY_CONTAIN",
        "FACILITY",
        "SYNONYM",
        "POSSIBLE_SYNONYM",
        "CLASS_RISK",
        "NOT_FOUND",
        "INSUFFICIENT",
        "OCR_UNCERTAIN",
        "USER_CONFIRM_REQUIRED",
    }


def test_severity_mapping_matches_policy_headers() -> None:
    # (status, severity) pairs read directly from ALLERGEN_POLICY section headers.
    expected = {
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
    assert expected == SEVERITY_BY_STATUS


def test_user_confirm_required_has_no_evidence_severity() -> None:
    # It is a pre-evidence gate, not an evidence severity.
    assert AllergenStatusCode.USER_CONFIRM_REQUIRED not in SEVERITY_BY_STATUS


def test_severity_display_order() -> None:
    # ALLERGEN_POLICY: positive findings first, negatives last.
    assert SEVERITY_DISPLAY_ORDER == (
        Severity.S1,
        Severity.S2,
        Severity.S3,
        Severity.S4,
        Severity.S5,
        Severity.S0,
    )


def test_severity_values() -> None:
    assert {s.value for s in Severity} == {"S0", "S1", "S2", "S3", "S4", "S5"}


def test_info_type_seven_way() -> None:
    assert {t.value for t in InfoType} == {
        "observed",
        "retrieved",
        "predicted",
        "user_provided",
        "estimated",
        "missing",
        "warning",
    }


def test_scan_mode_values() -> None:
    assert {m.value for m in ScanMode} == {"photo", "label", "panel", "barcode"}


def test_scan_state_includes_happy_path_and_failures() -> None:
    values = {s.value for s in ScanState}
    # Happy path from the state-machine doc.
    for expected in [
        "created",
        "uploaded",
        "quality_checked",
        "classifying",
        "ocr_running",
        "barcode_lookup",
        "awaiting_confirmation",
        "confirmed",
        "enriched",
        "enrichment_partial",
        "complete",
    ]:
        assert expected in values
    # Failure branches exist.
    for expected in ["classification_failed", "ocr_failed", "failed"]:
        assert expected in values


def test_evidence_source_values() -> None:
    assert {e.value for e in EvidenceSource} == {"ocr", "off", "class_hint"}


def test_data_source_kinds() -> None:
    assert {d.value for d in DataSourceKind} == {"fdc", "off", "user_ocr", "curated"}


def test_error_codes_exact_set() -> None:
    assert {c.value for c in ErrorCode} == {
        "validation_error",
        "unauthorized",
        "forbidden",
        "not_found",
        "conflict",
        "rate_limited",
        "provider_unavailable",
        "processing_failed",
        "quota_degraded",
    }


def test_error_envelope_roundtrip() -> None:
    env = ErrorEnvelope(
        error=ErrorDetail(code=ErrorCode.NOT_FOUND, message="scan not found", request_id="req-1")
    )
    dumped = env.model_dump()
    assert dumped == {
        "error": {"code": "not_found", "message": "scan not found", "request_id": "req-1"}
    }
    assert ErrorEnvelope.model_validate(dumped) == env


def test_error_envelope_rejects_unknown_code() -> None:
    with pytest.raises(ValidationError):
        ErrorEnvelope.model_validate(
            {"error": {"code": "not_a_real_code", "message": "x", "request_id": None}}
        )


def test_error_detail_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ErrorDetail.model_validate(
            {"code": "not_found", "message": "x", "request_id": None, "surprise": 1}
        )
