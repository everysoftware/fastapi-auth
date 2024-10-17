from app.config import settings
from app.context import users_ctx


async def register_users() -> None:
    async with users_ctx() as users:
        # Register admin
        user = await users.get_by_email(settings.auth.admin_email)
        if not user:
            await users.register(
                email=settings.auth.admin_email,
                password=settings.auth.admin_password,
                is_superuser=True,
                is_verified=True,
            )

        # Register first user
        user = await users.get_by_email(settings.auth.first_user_email)
        if not user:
            await users.register(
                email=settings.auth.first_user_email,
                password=settings.auth.first_user_password,
                is_verified=True,
            )
