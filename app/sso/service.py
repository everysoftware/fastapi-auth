from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.db.uow import UOW
from app.oidc.base import SSOProvider
from app.oidc.schemas import SSOCallback
from app.service import Service
from app.sso.exceptions import (
    SSOAlreadyAssociatedThisUser,
    SSOAlreadyAssociatedAnotherUser,
    SSOAccountNotFound,
)
from app.sso.schemas import SSOAccountRead
from app.users.schemas import UserRead
from app.users.service import UserService


class SSOAccountService(Service):
    users: UserService

    def __init__(self, uow: UOW, users: UserService):
        super().__init__(uow)
        self.users = users

    async def get(self, account_id: ID) -> SSOAccountRead | None:
        return await self.uow.sso_accounts.get(account_id)

    async def get_one(self, account_id: ID) -> SSOAccountRead:
        account = await self.uow.sso_accounts.get(account_id)
        if not account:
            raise SSOAccountNotFound()
        return account

    async def connect(
        self, user: UserRead, provider: SSOProvider, callback: SSOCallback
    ) -> SSOAccountRead:
        data = await self.users.get_sso_account(provider, callback)
        account = await self.uow.sso_accounts.get_by_account_id(
            provider.provider, data["account_id"]
        )
        if account:
            if account.user_id == user.id:
                raise SSOAlreadyAssociatedThisUser()
            else:
                raise SSOAlreadyAssociatedAnotherUser()
        return await self.uow.sso_accounts.create(user_id=user.id, **data)

    async def paginate(
        self, user: UserRead, params: PageParams
    ) -> Page[SSOAccountRead]:
        return await self.uow.sso_accounts.get_many_by_user_id(user.id, params)

    async def delete(self, account: SSOAccountRead) -> SSOAccountRead:
        return await self.uow.sso_accounts.delete(account.id)
