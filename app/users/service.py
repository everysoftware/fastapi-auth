import random
import secrets
import string
import uuid
from typing import assert_never, Any

from jwt import InvalidTokenError

from app.config import settings
from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.exceptions import InvalidRequest
from app.security.hashing import crypt_ctx
from app.security.tokens import encode_jwt, decode_jwt
from app.service import Service
from app.sso.dependencies import SSOName
from app.sso_accounts.schemas import SSOAccountRead, SSOAccountCreate
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
    UserTelegramNotFound,
    VerifyTokenRequired,
)
from app.users.forms import AuthorizationForm
from app.users.schemas import (
    UserUpdate,
    UserRead,
    Role,
    BearerToken,
    TokenType,
    GrantType,
    NotifyVia,
    ResetPassword,
    VerifyToken,
)
from app.users.tokens import (
    access_params,
    refresh_params,
    get_token_params,
    verify_params,
)


class UserService(Service):
    async def get_by_email(self, email: str) -> UserRead | None:
        return await self.uow.users.get_by_email(email)

    async def get_one_by_email(self, email: str) -> UserRead:
        user = await self.get_by_email(email)
        if not user:
            raise UserEmailNotFound()
        return user

    async def register(
        self,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        telegram_id: int | None = None,
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
            telegram_id=telegram_id,
        )
        if not is_verified:
            await self.send_code(via=NotifyVia.email, email=email)
        return user

    async def get(self, user_id: ID) -> UserRead | None:
        return await self.uow.users.get(user_id)

    async def get_one(self, user_id: ID) -> UserRead:
        user = await self.get(user_id)
        if not user:
            raise UserNotFound()
        return user

    async def update(
        self,
        user: UserRead,
        update: UserUpdate,
        verify_token: str | None = None,
    ) -> UserRead:
        if (
            update.password is not None
            or update.email is not None
            or update.is_verified is not None
        ):
            if verify_token is None:
                raise VerifyTokenRequired()
            await self.validate_token(
                verify_token, token_type=TokenType.verify
            )
        update_data = update.model_dump(
            exclude={"password"},
            exclude_none=True,
        )
        if update.password is not None:
            update_data["hashed_password"] = crypt_ctx.hash(update.password)
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

    async def send_code_email(self, email: str | None) -> None:
        if email is None:
            InvalidRequest("Email is not set")
        user = await self.get_one_by_email(email)
        code = await self.create_code(user)
        self.background.add_task(
            self.mail.send,
            user,
            "Your verification code",
            "code",
            code=code,  # noqa
        )

    async def send_code_telegram(self, telegram_id: int | None) -> None:
        if telegram_id is None:
            InvalidRequest("Telegram is not connected")
        user = await self.uow.users.get_by_telegram_id(telegram_id)
        if user is None:
            raise UserTelegramNotFound()
        code = await self.create_code(user)
        self.background.add_task(
            self.bot.send_message,
            telegram_id,
            f"Your verification code: {code}",
        )  # noqa

    async def send_code(
        self,
        *,
        via: NotifyVia = NotifyVia.email,
        email: str | None = None,
        telegram_id: int | None = None,
    ) -> None:
        match via:
            case NotifyVia.email:
                await self.send_code_email(email)
            case NotifyVia.telegram:
                await self.send_code_telegram(telegram_id)
            case _:
                assert_never(via)

    async def validate_code(self, user: UserRead, code: str) -> None:
        user_code = await self.cache.get(f"codes:{user.id}", cast=str)
        if user_code is None:
            raise WrongCode()
        if not secrets.compare_digest(user_code, code):
            raise WrongCode()
        await self.cache.delete(f"codes:{user.id}")

    async def verify_code(self, user: UserRead, code: str) -> VerifyToken:
        await self.validate_code(user, code)
        return VerifyToken(
            verify_token=encode_jwt(verify_params, subject=str(user.id)),
            expires_in=verify_params.expires_in.total_seconds(),
        )

    async def reset_password(self, reset: ResetPassword) -> UserRead:
        user = await self.get_one_by_email(reset.email)
        await self.validate_code(user, reset.code)
        return await self.uow.users.update(
            user.id, hashed_password=crypt_ctx.hash(reset.password)
        )

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

    async def get_login_url(
        self, provider: SSOName, redirect_uri: str, state: str
    ) -> str:
        sso = self.resolve_sso(provider)
        return await sso.get_login_url(redirect_uri=redirect_uri, state=state)

    async def sso_callback(
        self, provider: SSOName, callback: Any
    ) -> SSOAccountCreate:
        sso = self.resolve_sso(provider)
        token = await sso.login(callback)
        open_id = await sso.get_userinfo()
        return SSOAccountCreate(
            account_id=open_id.id,
            **open_id.model_dump(exclude={"id"}),
            **token.model_dump(exclude={"token_type"}),
        )

    async def sso_register(self, data: SSOAccountCreate) -> UserRead:
        # Check if user already exists
        user = None
        if data.email:
            user = await self.get_by_email(data.email)
        # If not, register new user
        if not user:
            telegram_id = (
                int(data.account_id) if data.provider == "telegram" else None
            )
            user = await self.register(
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                telegram_id=telegram_id,
                is_verified=True,
            )
        await self.uow.sso_accounts.create(
            user_id=user.id, **data.model_dump()
        )
        return user

    async def sso_authorize(
        self,
        data: SSOAccountCreate,
    ) -> BearerToken:
        account = await self.uow.sso_accounts.get_by_account(
            data.provider, data.account_id
        )
        if account:
            account = await self.uow.sso_accounts.update(
                account.id, **data.model_dump()
            )
            user = await self.get_one(account.user_id)
        else:
            user = await self.sso_register(data)
        return self.create_token(user)

    async def sso_connect(
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
        if data.provider == "telegram":
            await self.uow.users.update(
                user.id, telegram_id=int(data.account_id)
            )
        return await self.uow.sso_accounts.create(
            user_id=user.id, **data.model_dump()
        )
