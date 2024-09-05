import uuid
from typing import assert_never

from jwt import InvalidTokenError

from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.logging import logger
from app.service import Service
from app.sso.base import SSOProvider
from app.sso.schemas import SSOCallback
from app.users.auth import AuthorizationForm
from app.users.exceptions import (
    UserAlreadyExists,
    UserEmailNotFound,
    WrongPassword,
    InvalidToken,
    InvalidTokenType,
    UserNotFound,
)
from app.users.hashing import pwd_context
from app.users.schemas import (
    UserCreate,
    UserUpdate,
    UserRead,
    Role,
    BearerToken,
    TokenType,
    GrantType,
)
from app.users.tokens import (
    decode_jwt,
    access_params,
    refresh_params,
    encode_jwt,
)


class UserService(Service):
    async def register(
        self,
        data: UserCreate,
        is_verified: bool = False,
        is_superuser: bool = False,
    ) -> UserRead:
        user = await self.uow.users.get_by_email(data.email)
        if user:
            raise UserAlreadyExists()
        user_dict = data.model_dump()
        user_dict["hashed_password"] = pwd_context.hash(
            user_dict.pop("password")
        )
        user = await self.uow.users.create(
            **user_dict, is_verified=is_verified, is_superuser=is_superuser
        )
        # TODO: Send email confirmation
        return user

    async def get(self, user_id: ID) -> UserRead | None:
        return await self.uow.users.get(user_id)

    async def get_by_email(self, email: str) -> UserRead | None:
        return await self.uow.users.get_by_email(email)

    async def update(self, user_id: ID, update: UserUpdate) -> UserRead:
        update_data = update.model_dump(
            exclude_none=True,
        )
        if update.password is not None:
            update_data["hashed_password"] = pwd_context.hash(
                update_data.pop("password")
            )
        return await self.uow.users.update(user_id, **update_data)

    async def delete(self, user_id: ID) -> UserRead:
        return await self.uow.users.delete(user_id)

    # AUTHORIZATION
    @staticmethod
    def create_token(
        user: UserRead,
    ) -> BearerToken:
        """Issue bearer token for user."""
        access_token = encode_jwt(
            access_params, subject=str(user.id), email=user.email
        )
        refresh_token = encode_jwt(refresh_params, subject=str(user.id))
        return BearerToken(
            token_id=str(uuid.uuid4()),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(refresh_params.expires_in.total_seconds()),
        )

    async def login(
        self,
        form: AuthorizationForm,
    ) -> UserRead:
        # Identification
        user = await self.get_by_email(form.username)
        if not user:
            raise UserEmailNotFound()
        # Authentication
        if not pwd_context.verify(form.password, user.hashed_password):
            raise WrongPassword()
        return user

    async def validate_token(
        self, token: str, token_type: TokenType = TokenType.access
    ) -> UserRead:
        params = (
            access_params if token_type == TokenType.access else refresh_params
        )
        try:
            payload = decode_jwt(params, token)
        except InvalidTokenError as e:
            raise InvalidToken() from e
        if payload.typ != token_type:
            raise InvalidTokenType()
        user = await self.get(uuid.UUID(payload.sub, version=4))
        if user is None:
            raise UserNotFound()
        return user

    async def validate_rt(self, form: AuthorizationForm) -> UserRead:
        return await self.validate_token(form.refresh_token, TokenType.refresh)

    @staticmethod
    async def sso_login(
        provider: SSOProvider, redirect_uri: str | None = None
    ) -> str:
        return await provider.get_login_url(redirect_uri=redirect_uri)

    async def sso_callback(
        self, provider: SSOProvider, callback: SSOCallback
    ) -> BearerToken:
        open_id = await provider.verify_and_process(callback)
        assert open_id and open_id.email
        logger.info(open_id.model_dump())

        user = await self.get_by_email(open_id.email)
        if user:
            # TODO: Associate user with oauth account if not already
            # Else Update user's oauth account with new access token
            pass
        else:
            user = await self.register(
                UserCreate(email=open_id.email, password=uuid.uuid4().hex),
                is_verified=True,
            )
            # TODO: Associate user with oauth account

        return self.create_token(user)

    async def authorize(self, form: AuthorizationForm) -> BearerToken:
        match form.grant_type:
            case GrantType.password:
                user = await self.login(form)
            case GrantType.refresh_token:
                user = await self.validate_rt(form)
            case _:
                assert_never(form.grant_type)
        return self.create_token(user)

    # ADMIN
    async def get_many(self, params: PageParams) -> Page[UserRead]:
        return await self.uow.users.get_many(params)

    async def grant(self, user_id: ID, role: Role) -> UserRead:
        match role:
            case Role.user:
                update_data = {"is_superuser": False}
            case Role.superuser:
                update_data = {"is_superuser": True}
            case _:
                assert_never(role)
        return await self.uow.users.update(user_id, **update_data)
