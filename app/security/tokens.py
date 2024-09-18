import datetime
import uuid
from typing import Any

import jwt
from pydantic import Field, EmailStr, field_serializer, ConfigDict

from app.schemas import BackendBase


class TokenParams(BackendBase):
    issuer: str | None = None
    audience: list[str] | None = None
    algorithm: str = "HS256"
    private_key: str
    public_key: str
    type: str | None = None
    expires_in: datetime.timedelta
    include: set[str] | None = None
    exclude: set[str] | None = None


class JWTClaims(BackendBase):
    jti: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    iss: str | None = None
    aud: list[str] | None = None
    typ: str | None = None
    sub: str | None = None
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    iat: datetime.datetime | None = None
    nbf: datetime.datetime | None = None
    exp: datetime.datetime | None = None

    @field_serializer("iat", "exp", "nbf", mode="plain")
    def datetime_to_timestamp(
        self, value: datetime.datetime | None
    ) -> int | None:
        if value is None:
            return value
        return int(value.timestamp())

    model_config = ConfigDict(extra="allow")


def encode_jwt(
    params: TokenParams,
    *,
    subject: str,
    email: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    display_name: str | None = None,
    **payload: Any,
) -> str:
    now = datetime.datetime.now(datetime.UTC)
    claims = JWTClaims(
        iss=params.issuer,
        aud=params.audience,
        typ=params.type,
        sub=subject,
        iat=now,
        nbf=now,
        exp=now + params.expires_in,
        email=email,
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
        **payload,
    )
    encoded = jwt.encode(
        claims.model_dump(
            mode="json",
            exclude_none=True,
            include=params.include,
            exclude=params.exclude,
        ),
        params.private_key,
        algorithm=params.algorithm,
    )
    return encoded


def decode_jwt(params: TokenParams, token: str) -> JWTClaims:
    decoded = jwt.decode(
        token,
        params.public_key,
        algorithms=[params.algorithm],
        issuer=params.issuer,
        audience=params.audience,
    )
    return JWTClaims.model_validate(decoded)
