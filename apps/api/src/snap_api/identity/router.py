"""Authentication endpoints (docs/architecture/API_DESIGN.md §Authentication).

T-007: register + verify-email. T-008: login + refresh + logout + me. Rate limits
(per-IP/user) are applied centrally in T-054.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from snap_api.audit.repo import AuditRepo
from snap_api.core.db import get_session
from snap_api.core.errors import ApiError
from snap_api.identity.deps import get_current_user
from snap_api.identity.email import EmailSender, get_email_sender
from snap_api.identity.models import User
from snap_api.identity.repo import IdentityRepo
from snap_api.identity.schemas import (
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    MeResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from snap_api.identity.service import IdentityService, InvalidTokenError, IssuedTokens

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _service(
    session: AsyncSession = Depends(get_session),
    email_sender: EmailSender = Depends(get_email_sender),
) -> IdentityService:
    return IdentityService(IdentityRepo(session), email_sender, AuditRepo(session))


def _tokens_response(tokens: IssuedTokens) -> TokenResponse:
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
    service: IdentityService = Depends(_service),
) -> RegisterResponse:
    await service.register(email=str(body.email), password=body.password)
    await session.commit()
    return RegisterResponse()


@router.post("/verify-email")
async def verify_email(
    body: VerifyEmailRequest,
    session: AsyncSession = Depends(get_session),
    service: IdentityService = Depends(_service),
) -> VerifyEmailResponse:
    try:
        await service.verify_email(token=body.token)
    except InvalidTokenError:
        await session.rollback()
        raise ApiError.validation("Invalid or expired verification token.") from None
    await session.commit()
    return VerifyEmailResponse()


@router.post("/login")
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
    service: IdentityService = Depends(_service),
) -> TokenResponse:
    try:
        tokens = await service.login(
            email=str(body.email), password=body.password, device_label=body.device_label
        )
    except ApiError:
        # Persist failed-login bookkeeping (counters / lockout) before surfacing.
        await session.commit()
        raise
    await session.commit()
    return _tokens_response(tokens)


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),
    service: IdentityService = Depends(_service),
) -> TokenResponse:
    try:
        tokens = await service.refresh(refresh_token=body.refresh_token)
    except ApiError:
        # Persist family revocation (reuse detection) before surfacing.
        await session.commit()
        raise
    await session.commit()
    return _tokens_response(tokens)


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    session: AsyncSession = Depends(get_session),
    service: IdentityService = Depends(_service),
) -> LogoutResponse:
    await service.logout(refresh_token=body.refresh_token)
    await session.commit()
    return LogoutResponse()


@router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def password_reset(
    body: PasswordResetRequest,
    session: AsyncSession = Depends(get_session),
    service: IdentityService = Depends(_service),
) -> PasswordResetRequestResponse:
    await service.request_password_reset(email=str(body.email))
    await session.commit()
    return PasswordResetRequestResponse()


@router.post("/password-reset/confirm")
async def password_reset_confirm(
    body: PasswordResetConfirmRequest,
    session: AsyncSession = Depends(get_session),
    service: IdentityService = Depends(_service),
) -> PasswordResetConfirmResponse:
    try:
        await service.confirm_password_reset(token=body.token, new_password=body.new_password)
    except ApiError:
        await session.rollback()
        raise
    await session.commit()
    return PasswordResetConfirmResponse()


@router.get("/me")
async def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        email_verified=user.email_verified,
    )
