from sqlalchemy import select

from app.db.repository import AlchemyGenericRepository
from app.sso.models import SSOAccountOrm
from app.sso.schemas import OIDCAccountRead


class SSOAccountRepository(
    AlchemyGenericRepository[SSOAccountOrm, OIDCAccountRead]
):
    model_type = SSOAccountOrm
    schema_type = OIDCAccountRead

    async def get_by_account_id(
        self, provider: str, account_id: str
    ) -> OIDCAccountRead | None:
        stmt = select(SSOAccountOrm).where(
            (SSOAccountOrm.provider == provider)  # noqa
            & (SSOAccountOrm.account_id == account_id)
        )
        result = await self.session.scalar(stmt)
        if result is None:
            return None
        return OIDCAccountRead.model_validate(result)
