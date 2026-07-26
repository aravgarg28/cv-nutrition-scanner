"""Authentication endpoints (docs/architecture/API_DESIGN.md §Authentication).

T-007: register + verify-email. Login/refresh/reset land in T-008/T-009.
Rate limits (5/hr/IP register, etc.) are applied centrally in T-054.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from snap_api.core.db import get_session
from snap_api.identity.email import EmailSender, get_email_sender
from snap_api.identity.repo import IdentityRepo
from snap_api.identity.schemas import (
    RegisterRequest,
    RegisterResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from snap_api.identity.service import IdentityService, InvalidTokenError

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _service(
    session: AsyncSession = Depends(get_session),
    email_sender: EmailSender = Depends(get_email_sender),
) -> IdentityService:
    return IdentityService(IdentityRepo(session), email_sender)


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
        # Generic message; do not reveal which of missing/expired/used applies.
        from snap_api.core.errors import ApiError

        raise ApiError.validation("Invalid or expired verification token.") from None
    await session.commit()
    return VerifyEmailResponse()
