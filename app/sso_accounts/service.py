from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.service import Service
from app.sso_accounts.exceptions import (
    SSOAccountNotFound,
)
from app.sso_accounts.schemas import SSOAccountRead
from app.users.schemas import UserRead


class SSOAccountService(Service):
    async def get(self, account_id: ID) -> SSOAccountRead | None:
        return await self.uow.sso_accounts.get(account_id)

    async def get_one(self, account_id: ID) -> SSOAccountRead:
        account = await self.uow.sso_accounts.get(account_id)
        if not account:
            raise SSOAccountNotFound()
        return account

    async def paginate(
        self, user: UserRead, params: PageParams
    ) -> Page[SSOAccountRead]:
        return await self.uow.sso_accounts.get_many_by_user_id(user.id, params)

    async def delete(self, account: SSOAccountRead) -> SSOAccountRead:
        return await self.uow.sso_accounts.delete(account.id)
