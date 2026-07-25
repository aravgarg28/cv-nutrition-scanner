"""Canonical API error envelope (docs/architecture/API_DESIGN.md).

Every error response is `{"error": {"code", "message", "request_id"}}` with a code
from the closed ErrorCode set. `message` is safe for display (never leaks internal
detail or third-party provider text — see docs/ai/PROMPT_INJECTION_DEFENSE.md).
"""

from pydantic import BaseModel, ConfigDict

from snap_shared_schemas.enums import ErrorCode


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ErrorCode
    message: str
    request_id: str | None = None


class ErrorEnvelope(BaseModel):
    """Top-level error response body."""

    model_config = ConfigDict(extra="forbid")

    error: ErrorDetail
