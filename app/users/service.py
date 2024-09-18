import random
import secrets
import string
import uuid
from typing import assert_never

from jwt import InvalidTokenError

from app.cache.dependencies import CacheDep
from app.config import settings
from app.db.dependencies import UOWDep
from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.notifications.dependencies import NotificationServiceDep
from app.schemas import BackendOK, backend_ok
from app.security.hashing import crypt_ctx
from app.security.tokens import encode_jwt, decode_jwt
from app.service import Service
from app.sso.base import SSOBase
from app.sso.schemas import SSOCallback
from app.sso_accounts.schemas import SSOAccountRead, SSOAccountCreate
from app.users.forms import AuthorizationForm
from app.users.exceptions import (
    UserAlreadyExists,
    UserEmailNotFound,
    WrongPassword,
    InvalidToken,
    InvalidTokenType,
    UserNotFound,
    WrongCode,
    SSOAlreadyAssociatedThisUser,
    SSOAlreadyAssociatedAnotherUser,
    TelegramNotConnected,
    EmailNotSet,
)
from app.users.schemas import (
    UserUpdate,
    UserRead,
    Role,
    BearerToken,
    TokenType,
    GrantType,
    NotifyVia,
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
        hashed_password = crypt_ctx.hash(password) if password else None
        user = await self.uow.users.create(
            email=email,
            hashed_password=hashed_password,
            is_verified=is_verified,
            is_superuser=is_superuser,
            first_name=first_name,
            last_name=last_name,
        )
        try:
            await self.send_code(user, NotifyVia.email)
        except EmailNotSet:
            pass
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
            access_params,
            subject=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
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
        if not crypt_ctx.verify(form.password, user.hashed_password):
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
                assert form.refresh_token
                user = await self.refresh_token(form.refresh_token)
            case _:
                assert_never(form.grant_type)
        return self.create_token(user)

    async def create_code(self, user: UserRead) -> str:
        code = "".join(
            random.choices(string.digits, k=settings.auth.code_length)
        )
        await self.cache.add(
            f"codes:{user.id}", code, expire=settings.auth.code_expire
        )
        return code

    async def send_code(self, user: UserRead, via: NotifyVia) -> BackendOK:
        code = await self.create_code(user)
        match via:
            case NotifyVia.email:
                if user.email is None:
                    raise EmailNotSet()
                await self.notifications.send_email(
                    user,
                    "Your verification code",
                    "code",
                    code=code,
                )
            case NotifyVia.telegram:
                account = await self.uow.sso_accounts.get_by_user(
                    "telegram", user.id
                )
                if account is None:
                    raise TelegramNotConnected()
                await self.notifications.send_telegram(
                    account.account_id, f"Your verification code: {code}"
                )
            case _:
                assert_never(via)
        return backend_ok

    async def validate_code(self, user: UserRead, code: str) -> BackendOK:
        user_code = await self.cache.get(f"codes:{user.id}", cast=str)
        if user_code is None:
            raise WrongCode()
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
    async def get_data_from_provider(
        provider: SSOBase, callback: SSOCallback
    ) -> SSOAccountCreate:
        sso_token = await provider.login(callback)
        user_info = await provider.get_userinfo()
        return SSOAccountCreate(
            account_id=user_info.id,
            **user_info.model_dump(exclude={"id"}),
            **sso_token.model_dump(exclude={"token_type"}),
        )

    async def authorize_sso(
        self,
        data: SSOAccountCreate,
    ) -> BearerToken:
        account = await self.uow.sso_accounts.get_by_account(
            data.provider, data.account_id
        )
        user = None
        data_dict = data.model_dump()
        if account:
            account = await self.uow.sso_accounts.update(
                account.id, **data_dict
            )
            user = await self.get_one(account.user_id)
        else:
            if data.email:
                user = await self.get_by_email(data.email)
            if not user:
                user = await self.register(
                    first_name=data.first_name,
                    last_name=data.last_name,
                    email=data.email,
                    is_verified=True,
                )
            await self.uow.sso_accounts.create(user_id=user.id, **data_dict)
        return self.create_token(user)

    async def connect(
        self,
        user: UserRead,
        data: SSOAccountCreate,
    ) -> SSOAccountRead:
        account = await self.uow.sso_accounts.get_by_account(
            data.provider, data.account_id
        )
        if account:
            if account.user_id == user.id:
                raise SSOAlreadyAssociatedThisUser()
            else:
                raise SSOAlreadyAssociatedAnotherUser()
        return await self.uow.sso_accounts.create(
            user_id=user.id, **data.model_dump()
        )
