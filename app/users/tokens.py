import datetime

import jwt

from app.config import settings
from app.users.schemas import (
    TokenType,
    TokenParams,
    JWTClaims,
)

access_params = TokenParams(
    type=TokenType.access,
    expires_in=datetime.timedelta(
        minutes=settings.auth.jwt_access_expire_minutes
    ),
)
refresh_params = TokenParams(
    type=TokenType.refresh,
    expires_in=datetime.timedelta(
        minutes=settings.auth.jwt_refresh_expire_minutes
    ),
)


def encode_jwt(
    params: TokenParams,
    *,
    subject: str,
    email: str | None = None,
) -> str:
    now = datetime.datetime.now(datetime.UTC)
    payload = JWTClaims(
        iss=params.issuer,
        aud=params.audience,
        typ=params.type,
        sub=subject,
        iat=now,
        nbf=now,
        exp=now + params.expires_in,
        email=email,
    )
    encoded = jwt.encode(
        payload.model_dump(mode="json", exclude_none=True),
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
