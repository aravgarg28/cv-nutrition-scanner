"""Application error type and handlers that render the canonical error envelope.

Every error response is `{"error": {"code", "message", "request_id"}}` with a code
from the closed ErrorCode set (docs/architecture/API_DESIGN.md).
"""

from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from snap_api.identity.password_policy import PasswordPolicyError
from snap_shared_schemas import ErrorCode, ErrorDetail, ErrorEnvelope

HTTP_422 = 422  # Unprocessable content (avoids a deprecated Starlette constant).


class ApiError(Exception):
    """Raise to return a typed error envelope with the given HTTP status."""

    def __init__(self, *, code: ErrorCode, message: str, http_status: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status

    @classmethod
    def validation(cls, message: str) -> ApiError:
        return cls(code=ErrorCode.VALIDATION_ERROR, message=message, http_status=HTTP_422)

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized.") -> ApiError:
        return cls(code=ErrorCode.UNAUTHORIZED, message=message, http_status=401)

    @classmethod
    def locked(cls, message: str) -> ApiError:
        # Too many attempts; 423 Locked with the rate-limited code.
        return cls(code=ErrorCode.RATE_LIMITED, message=message, http_status=423)


def _envelope(request: Request, code: ErrorCode, message: str, http_status: int) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    body = ErrorEnvelope(error=ErrorDetail(code=code, message=message, request_id=request_id))
    return JSONResponse(status_code=http_status, content=body.model_dump())


async def _handle_api_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ApiError)
    return _envelope(request, exc.code, exc.message, exc.http_status)


async def _handle_password_policy(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, PasswordPolicyError)
    return _envelope(request, ErrorCode.VALIDATION_ERROR, exc.message, HTTP_422)


async def _handle_request_validation(request: Request, exc: Exception) -> JSONResponse:
    return _envelope(
        request,
        ErrorCode.VALIDATION_ERROR,
        "Invalid request.",
        HTTP_422,
    )


def register_error_handlers(app) -> None:  # noqa: ANN001  (FastAPI app)
    app.add_exception_handler(ApiError, _handle_api_error)
    app.add_exception_handler(PasswordPolicyError, _handle_password_policy)
    app.add_exception_handler(RequestValidationError, _handle_request_validation)
