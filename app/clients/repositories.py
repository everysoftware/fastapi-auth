from sqlalchemy import select

from app.clients.models import ClientOrm
from app.clients.schemas import ClientRead
from app.db.repository import AlchemyRepository


class ClientRepository(AlchemyRepository[ClientOrm, ClientRead]):
    model_type = ClientOrm
    schema_type = ClientRead

    async def get_by_client_id(self, client_id: str) -> ClientRead | None:
        stmt = select(self.model_type).where(
            self.model_type.client_id == client_id
        )
        result = await self.session.scalar(stmt)
        if result is None:
            return None
        return self.schema_type.model_validate(result)
