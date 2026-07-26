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
