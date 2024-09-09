import uuid
from typing import assert_never, Any

from jwt import InvalidTokenError
from pydantic import AnyHttpUrl

from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.oidc.base import SSOProvider
from app.oidc.schemas import SSOCallback
from app.service import Service
from app.sso.schemas import SSOAccountRead
from app.users.auth import AuthorizationForm
from app.users.exceptions import (
    UserAlreadyExists,
    UserEmailNotFound,
    WrongPassword,
    InvalidToken,
    InvalidTokenType,
    UserNotFound,
    SSOAlreadyAssociatedThisUser,
    SSOAlreadyAssociatedAnotherUser,
)
from app.users.hashing import pwd_context
from app.users.schemas import (
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
    async def get_by_email(self, email: str) -> UserRead | None:
        return await self.uow.users.get_by_email(email)

    async def register(
        self,
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
        )
        # TODO: Send email confirmation
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
        if update.password is not None:
            update_data["hashed_password"] = pwd_context.hash(
                update_data.pop("password")
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

    async def process_password_grant(
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

    async def process_rt_grant(self, form: AuthorizationForm) -> UserRead:
        assert form.refresh_token is not None
        return await self.validate_token(form.refresh_token, TokenType.refresh)

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

    async def sso_token(
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
            user = await self.get_by_email(data["email"])
            if not user:
                user = await self.register(
                    email=data["email"], is_verified=True
                )
            await self.uow.sso_accounts.create(user_id=user.id, **data)
        return self.create_token(user)

    async def sso_connect(
        self, user: UserRead, provider: SSOProvider, callback: SSOCallback
    ) -> SSOAccountRead:
        data = await self.get_sso_account(provider, callback)
        account = await self.uow.sso_accounts.get_by_account_id(
            provider.provider, data["account_id"]
        )
        if account:
            if account.user_id == user.id:
                raise SSOAlreadyAssociatedThisUser()
            else:
                raise SSOAlreadyAssociatedAnotherUser()
        return await self.uow.sso_accounts.create(user_id=user.id, **data)

    async def paginate_sso_accounts(
        self, user: UserRead, params: PageParams
    ) -> Page[SSOAccountRead]:
        return await self.uow.sso_accounts.get_many_by_user_id(user.id, params)

    async def authorize(self, form: AuthorizationForm) -> BearerToken:
        match form.grant_type:
            case GrantType.password:
                user = await self.process_password_grant(form)
            case GrantType.refresh_token:
                user = await self.process_rt_grant(form)
            case _:
                assert_never(form.grant_type)
        return self.create_token(user)

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
