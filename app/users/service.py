from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.database.uow import UOW
from app.service import Service
from app.users import jwt_helper
from app.users.exceptions import InvalidToken
from app.users.schemas import UserCreate, UserUpdate, UserRead, TokenInfo


class UserService(Service):
    pwd_context: CryptContext

    def __init__(self, uow: UOW):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        super().__init__(uow)

    async def register(self, creation: UserCreate) -> UserRead:
        user_data = creation.model_dump()
        user_data["hashed_password"] = self.pwd_context.hash(
            user_data.pop("password")
        )
        return await self.uow.users.create(**user_data)

    async def login(self, email: str, password: str) -> TokenInfo | None:
        user = await self.uow.users.get_by_email(email)
        if not user:
            return None
        if not self.pwd_context.verify(password, user.hashed_password):
            return None
        payload = {"type": "access", "sub": str(user.id)}
        access_token = jwt_helper.encode_jwt(payload)
        return TokenInfo(access_token=access_token)

    async def validate(self, access_token: str) -> UserRead:
        try:
            payload = jwt_helper.decode_jwt(access_token)
        except InvalidTokenError as e:
            raise InvalidToken from e
        if payload["type"] != "access":
            raise InvalidToken(f"Invalid token type: {payload["type"]}")
        user = await self.uow.users.get(payload["sub"])
        if user is None:
            raise InvalidToken(f"User {payload["sub"]} not found")
        return user

    async def get(self, user_id: str) -> UserRead | None:
        return await self.uow.users.get(user_id)

    async def get_by_email(self, email: str) -> UserRead | None:
        return await self.uow.users.get_by_email(email)

    async def update(self, user_id: str, update: UserUpdate) -> UserRead:
        update_data = update.model_dump(exclude_none=True)
        if update.password is not None:
            update_data["hashed_password"] = self.pwd_context.hash(
                update_data.pop("password")
            )
        return await self.uow.users.update(user_id, update_data)

    async def delete(self, user_id: str) -> UserRead:
        return await self.uow.users.delete(user_id)
