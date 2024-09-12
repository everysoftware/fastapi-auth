import random
import secrets
import uuid
from typing import assert_never, Any

from jwt import InvalidTokenError
from pydantic import AnyHttpUrl

from app.cache.dependencies import CacheDep
from app.config import settings
from app.db.dependencies import UOWDep
from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.notifications.dependencies import NotificationServiceDep
from app.oidc.base import SSOProvider
from app.oidc.schemas import SSOCallback
from app.schemas import BackendOK, backend_ok
from app.security.hashing import pwd_context
from app.security.tokens import encode_jwt, decode_jwt
from app.service import Service
from app.users.auth import AuthorizationForm
from app.users.exceptions import (
    UserAlreadyExists,
    UserEmailNotFound,
    WrongPassword,
    InvalidToken,
    InvalidTokenType,
    UserNotFound,
    CodeExpired,
    WrongCode,
)
from app.users.schemas import (
    UserUpdate,
    UserRead,
    Role,
    BearerToken,
    TokenType,
    GrantType,
)
from app.users.tokens import (
    access_params,
    refresh_params,
    get_token_params,
)


class UserService(Service):
    notifications: NotificationServiceDep

    def __init__(
        self,
        uow: UOWDep,
        cache: CacheDep,
        *,
        notifications: NotificationServiceDep,
    ):
        super().__init__(uow, cache)
        self.notifications = notifications

    async def get_by_email(self, email: str) -> UserRead | None:
        return await self.uow.users.get_by_email(email)

    async def register(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        is_verified: bool = False,
        is_superuser: bool = False,
    ) -> UserRead:
        if email and (await self.get_by_email(email)):
            raise UserAlreadyExists()
        hashed_password = pwd_context.hash(password) if password else None
        user = await self.uow.users.create(
            email=email,
            hashed_password=hashed_password,
            is_verified=is_verified,
            is_superuser=is_superuser,
            first_name=first_name,
            last_name=last_name,
        )
        await self.send_code(user)
        return user

    async def get(self, user_id: ID) -> UserRead | None:
        return await self.uow.users.get(user_id)

    async def get_one(self, user_id: ID) -> UserRead:
        user = await self.get(user_id)
        if not user:
            raise UserNotFound()
        return user

    async def update(self, user: UserRead, update: UserUpdate) -> UserRead:
        update_data = update.model_dump(
            exclude_none=True,
        )
        return await self.uow.users.update(user.id, **update_data)

    async def delete(self, user: UserRead) -> UserRead:
        return await self.uow.users.delete(user.id)

    @staticmethod
    def create_token(
        user: UserRead,
    ) -> BearerToken:
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

    async def authorize_password(
        self,
        form: AuthorizationForm,
    ) -> UserRead:
        user = await self.get_by_email(form.username)
        if not user:
            raise UserEmailNotFound()
        if not pwd_context.verify(form.password, user.hashed_password):
            raise WrongPassword()
        return user

    async def validate_token(
        self, token: str, token_type: TokenType = TokenType.access
    ) -> UserRead:
        params = get_token_params(token_type)
        try:
            payload = decode_jwt(params, token)
        except InvalidTokenError as e:
            raise InvalidToken() from e
        if payload.typ != token_type:
            raise InvalidTokenType()
        return await self.get_one(uuid.UUID(payload.sub, version=4))

    async def refresh_token(self, token: str) -> UserRead:
        return await self.validate_token(token, TokenType.refresh)

    async def authorize(self, form: AuthorizationForm) -> BearerToken:
        match form.grant_type:
            case GrantType.password:
                user = await self.authorize_password(form)
            case GrantType.refresh_token:
                user = await self.refresh_token(form.refresh_token)
            case _:
                assert_never(form.grant_type)
        return self.create_token(user)

    async def send_code(self, user: UserRead) -> BackendOK:
        code = "".join(
            random.choices("0123456789", k=settings.auth.code_length)
        )
        await self.cache.add(
            f"codes:{user.id}", code, expire=settings.auth.code_expire
        )
        await self.notifications.send_email(
            user,
            "Your verification code",
            "code",
            code=code,
        )
        return backend_ok

    async def validate_code(self, user: UserRead, code: str) -> BackendOK:
        user_code = await self.cache.get(f"codes:{user.id}", cast=str)
        if user_code is None:
            raise CodeExpired()
        if not secrets.compare_digest(user_code, code):
            raise WrongCode()
        await self.cache.delete(f"codes:{user.id}")
        return backend_ok

    async def verify(self, user: UserRead, code: str) -> UserRead:
        await self.validate_code(user, code)
        return await self.uow.users.update(user.id, is_verified=True)

    async def get_many(self, params: PageParams) -> Page[UserRead]:
        return await self.uow.users.get_many(params)

    async def grant(self, user: UserRead, role: Role) -> UserRead:
        match role:
            case Role.user:
                update_data = {"is_superuser": False}
            case Role.superuser:
                update_data = {"is_superuser": True}
            case _:
                assert_never(role)
        return await self.uow.users.update(user.id, **update_data)

    @staticmethod
    async def get_consent_url(
        provider: SSOProvider, redirect_uri: AnyHttpUrl, state: str
    ) -> str:
        return await provider.get_login_url(
            redirect_uri=redirect_uri, state=state
        )

    @staticmethod
    async def get_sso_account(
        provider: SSOProvider, callback: SSOCallback
    ) -> dict[str, Any]:
        sso_token = await provider.login(callback)
        user_info = await provider.get_userinfo()
        return {
            "account_id": user_info.id,
            **user_info.model_dump(exclude={"id"}),
            **sso_token.model_dump(exclude={"token_type"}),
        }

    async def authorize_sso(
        self, provider: SSOProvider, callback: SSOCallback
    ) -> BearerToken:
        data = await self.get_sso_account(provider, callback)
        account = await self.uow.sso_accounts.get_by_account_id(
            provider.provider, data["account_id"]
        )
        if account:
            account = await self.uow.sso_accounts.update(account.id, **data)
            user = await self.get_one(account.user_id)
        else:
            user = await self.get_by_email(data["email"])  # type: ignore[assignment]
            if not user:
                user = await self.register(
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    is_verified=True,
                )
            await self.uow.sso_accounts.create(user_id=user.id, **data)
        return self.create_token(user)
