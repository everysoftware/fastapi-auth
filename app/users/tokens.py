import datetime
from typing import TypedDict, Unpack

import jwt

from app.config import settings
from app.db.types import ID
from app.users.schemas import (
    TokenType,
    TokenParams,
    JWTPayload,
    EncodeJWTResponse,
)

access_params = TokenParams(
    type=TokenType.access,
    expires_in=datetime.timedelta(minutes=settings.jwt_access_expire_minutes),
)
refresh_params = TokenParams(
    type=TokenType.refresh,
    expires_in=datetime.timedelta(minutes=settings.jwt_refresh_expire_minutes),
)


class JWTArgs(TypedDict):
    token_id: str
    subject: ID
    issued_at: datetime.datetime
    expires_at: datetime.datetime


def encode_jwt(
    params: TokenParams,
    **kwargs: Unpack[JWTArgs],
) -> EncodeJWTResponse:
    payload = JWTPayload(
        jti=kwargs["token_id"],
        typ=params.type,
        sub=kwargs["subject"],
        iat=kwargs["issued_at"],
        exp=kwargs["expires_at"],
    )
    encoded = jwt.encode(
        payload.model_dump(mode="json"),
        params.private_key,
        algorithm=params.algorithm,
    )
    return EncodeJWTResponse(
        payload=JWTPayload.model_validate(payload), token=encoded
    )


def decode_jwt(params: TokenParams, token: str) -> JWTPayload:
    decoded = jwt.decode(
        token,
        params.public_key,
        algorithms=[params.algorithm],
    )
    return JWTPayload.model_validate(decoded)
