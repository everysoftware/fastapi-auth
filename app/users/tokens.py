import datetime
from typing import assert_never

from app.config import settings
from app.users.schemas import (
    TokenType,
    TokenParams,
)

access_params = TokenParams(
    type=TokenType.access,
    expires_in=datetime.timedelta(seconds=settings.auth.jwt_access_expire),
)
refresh_params = TokenParams(
    type=TokenType.refresh,
    expires_in=datetime.timedelta(seconds=settings.auth.jwt_refresh_expire),
)


def get_token_params(token_type: TokenType) -> TokenParams:
    match token_type:
        case TokenType.access:
            return access_params
        case TokenType.refresh:
            return refresh_params
        case _:
            assert_never(token_type)
