from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.context import users_ctx
from app.exceptions import BackendError
from app.users.auth import AuthorizationForm
from app.users.schemas import GrantType


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        data = await request.form()
        form = AuthorizationForm(
            grant_type=GrantType.password,
            username=data["username"],  # type: ignore[arg-type]
            password=data["password"],  # type: ignore[arg-type]
        )

        # Validate username/password credentials
        async with users_ctx() as users:
            try:
                user = await users.authorize_password(form)
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

        async with users_ctx() as users:
            try:
                user = await users.validate_token(token)
            except BackendError:
                return False
            if not user.is_superuser:
                return False
        return True


auth_backend = AdminAuth(secret_key="...")
