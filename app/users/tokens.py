import datetime
from typing import assert_never

from app.config import settings
from app.security.tokens import TokenParams
from app.users.schemas import (
    TokenType,
)

access_params = TokenParams(
    issuer=settings.auth.jwt_issuer,
    audience=settings.auth.jwt_audience,
    algorithm=settings.auth.jwt_algorithm,
    private_key=settings.auth.jwt_private_key.read_text(),
    public_key=settings.auth.jwt_public_key.read_text(),
    type=TokenType.access,
    expires_in=datetime.timedelta(seconds=settings.auth.jwt_access_expire),
)
refresh_params = TokenParams(
    issuer=settings.auth.jwt_issuer,
    audience=settings.auth.jwt_audience,
    algorithm=settings.auth.jwt_algorithm,
    private_key=settings.auth.jwt_private_key.read_text(),
    public_key=settings.auth.jwt_public_key.read_text(),
    type=TokenType.refresh,
    expires_in=datetime.timedelta(seconds=settings.auth.jwt_refresh_expire),
)
verify_params = TokenParams(
    issuer=settings.auth.jwt_issuer,
    audience=settings.auth.jwt_audience,
    algorithm=settings.auth.jwt_algorithm,
    private_key=settings.auth.jwt_private_key.read_text(),
    public_key=settings.auth.jwt_public_key.read_text(),
    type=TokenType.verify,
    expires_in=datetime.timedelta(seconds=settings.auth.code_expire),
)


def get_token_params(token_type: TokenType) -> TokenParams:
    match token_type:
        case TokenType.access:
            return access_params
        case TokenType.refresh:
            return refresh_params
        case TokenType.verify:
            return verify_params
        case _:
            assert_never(token_type)
