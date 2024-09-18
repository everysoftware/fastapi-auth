from typing import NoReturn, Annotated, assert_never

from fastapi import Form
from fastapi.security import (
    OAuth2PasswordRequestForm as FastAPIOAuth2PasswordRequestForm,
)

from app.exceptions import ValidationError
from app.users.schemas import GrantType


def raise_form_exc(msg: str) -> NoReturn:
    raise ValidationError(
        [
            {
                "loc": "form",
                "msg": msg,
            }
        ]
    )


class AuthorizationForm(FastAPIOAuth2PasswordRequestForm):
    grant_type: GrantType

    def __init__(
        self,
        *,
        grant_type: Annotated[
            GrantType,
            Form(),
        ],
        # Password
        username: Annotated[
            str | None,
            Form(
                examples=["user@example.com"],
            ),
        ] = None,
        password: Annotated[
            str | None,
            Form(examples=["password"]),
        ] = None,
        # Refresh token
        refresh_token: Annotated[str | None, Form()] = None,
    ):
        match grant_type:
            case GrantType.password:
                if not username or not password:
                    raise_form_exc("Username and password are required")
            case GrantType.refresh_token:
                if not refresh_token:
                    raise_form_exc("Refresh token is required")
            case _:
                assert_never(grant_type)

        self.refresh_token = refresh_token

        super().__init__(
            grant_type=grant_type,
            username=username,  # type: ignore[arg-type]
            password=password,  # type: ignore[arg-type]
            scope="",
            client_id="",
            client_secret="",
        )
