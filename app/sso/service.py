import uuid

from app.db.uow import UOW
from app.service import Service
from app.sso.providers.base import SSOProvider
from app.sso.providers.schemas import SSOCallback
from app.users.schemas import BearerToken, UserCreate
from app.users.service import UserService


class SSOService(Service):
    users: UserService

    def __init__(self, uow: UOW, *, users: UserService):
        super().__init__(uow)
        self.users = users

    @staticmethod
    async def sso_login(
        provider: SSOProvider, redirect_uri: str | None = None
    ) -> str:
        return await provider.get_login_url(redirect_uri=redirect_uri)

    async def sso_callback(
        self, provider: SSOProvider, callback: SSOCallback
    ) -> BearerToken:
        open_id = await provider.verify_and_process(callback)
        assert open_id and open_id.provider and open_id.email
        base_data = dict(
            access_token=provider.access_token,
            refresh_token=provider.refresh_token,
            id_token=provider.id_token,
            account_id=open_id.id,
            **open_id.model_dump(exclude={"id"}),
        )
        user = await self.users.get_by_email(open_id.email)
        account = None
        if user:
            account = await self.uow.oidc_accounts.get_by_provider_and_email(
                open_id.provider, open_id.email
            )
            if account:
                await self.uow.oidc_accounts.update(account.id, **base_data)
        else:
            user = await self.users.register(
                UserCreate(email=open_id.email, password=uuid.uuid4().hex),
                is_verified=True,
            )
        if not account:
            await self.uow.oidc_accounts.create(user_id=user.id, **base_data)
        return self.users.create_token(user)
