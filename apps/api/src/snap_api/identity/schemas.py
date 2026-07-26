"""Request/response models for identity endpoints.

These appear in the OpenAPI schema and therefore in the generated TS client
(T-005), so mobile/web never hand-type these shapes.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class RegisterResponse(BaseModel):
    # Enumeration-safe: identical whether or not the email already existed.
    status: str = "verification_sent"


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1, max_length=512)


class VerifyEmailResponse(BaseModel):
    status: str = "verified"


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=200)
    device_label: str | None = Field(default=None, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # access-token lifetime in seconds


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=1, max_length=512)


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=1, max_length=512)


class LogoutResponse(BaseModel):
    status: str = "ok"


class MeResponse(BaseModel):
    id: str
    email: str
    role: str
    email_verified: bool
