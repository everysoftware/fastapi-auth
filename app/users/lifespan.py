from app.config import settings
from app.db.connection import async_session_factory
from app.db.uow import UOW
from app.users.schemas import UserCreate, AccessType, UserRead
from app.users.service import UserService


async def register_superuser() -> UserRead:
    async with UOW(async_session_factory) as uow:
        users = UserService(uow)
        user = await users.get_by_email(settings.su_email)
        if not user:
            user = await users.register(
                UserCreate(
                    email=settings.su_email, password=settings.su_password
                )
            )
            user = await users.grant(user.id, AccessType.superuser)
        return user
