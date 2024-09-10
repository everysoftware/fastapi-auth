from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.db.connection import async_session_factory
from app.db.uow import UOW
from app.exceptions import BackendError
from app.users.auth import AuthorizationForm
from app.users.schemas import GrantType
from app.users.service import UserService


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        data = await request.form()
        form = AuthorizationForm(
            grant_type=GrantType.password,
            username=data["username"],
            password=data["password"],
        )

        # Validate username/password credentials
        async with UOW(async_session_factory) as uow:
            users = UserService(uow)
            try:
                user = await users.process_password_grant(form)
            except BackendError:
                return False
            if not user or not user.is_superuser:
                return False
            token = users.create_token(user)

        # And update session
        request.session.update({"token": token.access_token})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        async with UOW(async_session_factory) as uow:
            users = UserService(uow)
            try:
                user = await users.validate_token(token)
            except BackendError:
                return False
            if not user.is_superuser:
                return False
        return True


auth_backend = AdminAuth(secret_key="...")
