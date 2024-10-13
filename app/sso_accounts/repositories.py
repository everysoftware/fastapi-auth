from sqlalchemy import select

from app.db.repository import AlchemyRepository
from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.sso_accounts.models import SSOAccountOrm
from app.sso_accounts.schemas import SSOAccountRead


class SSOAccountRepository(AlchemyRepository[SSOAccountOrm, SSOAccountRead]):
    model_type = SSOAccountOrm
    schema_type = SSOAccountRead

    async def get_by_account(
        self, provider: str, account_id: str
    ) -> SSOAccountRead | None:
        stmt = select(SSOAccountOrm).where(
            (SSOAccountOrm.provider == provider)  # noqa
            & (SSOAccountOrm.account_id == account_id)
        )
        result = await self.session.scalar(stmt)
        if result is None:
            return None
        return SSOAccountRead.model_validate(result)

    async def get_by_user(
        self, provider: str, user_id: ID
    ) -> SSOAccountRead | None:
        stmt = select(SSOAccountOrm).where(
            (SSOAccountOrm.provider == provider)  # noqa
            & (SSOAccountOrm.user_id == user_id)
        )
        result = await self.session.scalar(stmt)
        if result is None:
            return None
        return SSOAccountRead.model_validate(result)

    async def paginate_by_user(
        self, user_id: ID, params: PageParams
    ) -> Page[SSOAccountRead]:
        stmt = select(SSOAccountOrm).where(SSOAccountOrm.user_id == user_id)  # noqa
        stmt = self.build_pagination_query(params, stmt)
        result = await self.session.scalars(stmt)
        return self.validate_page(result)
