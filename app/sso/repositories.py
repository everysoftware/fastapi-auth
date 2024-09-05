from sqlalchemy import select

from app.db.repository import AlchemyGenericRepository
from app.sso.models import OIDCAccountOrm
from app.sso.schemas import OIDCAccountRead


class OIDCAccountRepository(
    AlchemyGenericRepository[OIDCAccountOrm, OIDCAccountRead]
):
    model_type = OIDCAccountOrm
    schema_type = OIDCAccountRead

    async def get_by_provider_and_email(
        self, provider: str, email: str
    ) -> OIDCAccountRead | None:
        stmt = select(OIDCAccountOrm).where(
            (OIDCAccountOrm.provider == provider)  # noqa
            & (OIDCAccountOrm.email == email)
        )
        result = await self.session.scalar(stmt)
        if result is None:
            return None
        return OIDCAccountRead.model_validate(result)
