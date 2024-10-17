from app.config import settings
from app.context import uow_ctx
from app.db.uow import UOW


async def create_clients() -> None:
    async with uow_ctx() as uow:
        uow: UOW
        client = await uow.clients.get_by_client_id(settings.client.client_id)
        if not client:
            await uow.clients.create(
                name=settings.client.client_name,
                client_id=settings.client.client_id,
                client_secret=settings.client.client_secret,
                redirect_uris=";".join(settings.client.client_urls),
            )
