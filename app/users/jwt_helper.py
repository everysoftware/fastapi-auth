import uuid
from datetime import timedelta, datetime, UTC
from typing import Any

import jwt

from app.settings import settings


def encode_jwt(
    payload: dict[str, Any],
    private_key: str = settings.jwt_private_key.read_text(),
    algorithm: str = settings.jwt_algorithm,
    expire_minutes: int = settings.jwt_access_token_expire,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.jwt_public_key.read_text(),
    algorithm: str = settings.jwt_algorithm,
) -> dict[str, Any]:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded
