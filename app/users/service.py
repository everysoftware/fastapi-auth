import datetime
import uuid
from typing import assert_never

from jwt import InvalidTokenError

from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.service import Service
from app.users.exceptions import (
    UserAlreadyExists,
    UserEmailNotFound,
    WrongPassword,
    InvalidToken,
    InvalidTokenType,
    UserNotFound,
)
from app.users.hashing import pwd_context
from app.users.schemas import (
    UserCreate,
    UserUpdate,
    UserRead,
    Role,
    BearerToken,
    TokenType,
)
from app.users.tokens import (
    decode_jwt,
    access_params,
    refresh_params,
    encode_jwt,
    JWTArgs,
)


class UserService(Service):
    async def register(self, data: UserCreate) -> UserRead:
        user = await self.uow.users.get_by_email(data.email)
        if user:
            raise UserAlreadyExists()
        user_dict = data.model_dump()
        user_dict["hashed_password"] = pwd_context.hash(
            user_dict.pop("password")
        )
        return await self.uow.users.create(**user_dict)

    @staticmethod
    def issue_token(
        user: UserRead,
    ) -> BearerToken:
        """Issue bearer token for user."""
        now = datetime.datetime.now(datetime.UTC)
        args = JWTArgs(
            token_id=str(uuid.uuid4()),
            subject=str(user.id),
            issued_at=now,
            expires_at=now + refresh_params.expires_in,
        )
        access_response = encode_jwt(access_params, **args)
        refresh_response = encode_jwt(refresh_params, **args)
        return BearerToken(
            token_id=args["token_id"],
            access_token=access_response.token,
            refresh_token=refresh_response.token,
            expires_in=int(refresh_params.expires_in.total_seconds()),
        )

    async def authorize_by_password(
        self, email: str, password: str
    ) -> BearerToken:
        """
        Authorize user by email and password. Return bearer token that can be
        used to authenticate user in future requests.
        """
        # Identification
        user = await self.uow.users.get_by_email(email)
        if not user:
            raise UserEmailNotFound()
        # Authentication
        if not pwd_context.verify(password, user.hashed_password):
            raise WrongPassword()
        # Authorization
        return self.issue_token(user)

    async def validate_token(
        self, token: str, token_type: TokenType = TokenType.access
    ) -> UserRead:
        """Validate token and return user."""
        params = (
            access_params if token_type == TokenType.access else refresh_params
        )
        try:
            payload = decode_jwt(params, token)
        except InvalidTokenError as e:
            raise InvalidToken(message=str(e)) from e
        if payload.typ != token_type:
            raise InvalidTokenType()
        user = await self.uow.users.get(payload.sub)
        if user is None:
            raise UserNotFound()
        return user

    async def authorize_by_refresh_token(
        self, refresh_token: str
    ) -> BearerToken:
        """Refresh bearer token using refresh token."""
        user = await self.validate_token(refresh_token, TokenType.refresh)
        return self.issue_token(user)

    async def get(self, user_id: ID) -> UserRead | None:
        return await self.uow.users.get(user_id)

    async def get_by_email(self, email: str) -> UserRead | None:
        return await self.uow.users.get_by_email(email)

    async def update(self, user_id: ID, update: UserUpdate) -> UserRead:
        update_data = update.model_dump(exclude_none=True)
        if update.password is not None:
            update_data["hashed_password"] = pwd_context.hash(
                update_data.pop("password")
            )
        return await self.uow.users.update(user_id, **update_data)

    async def delete(self, user_id: ID) -> UserRead:
        return await self.uow.users.delete(user_id)

    async def get_many(self, params: PageParams) -> Page[UserRead]:
        return await self.uow.users.get_many(params)

    async def grant(self, user_id: ID, role: Role) -> UserRead:
        match role:
            case Role.user:
                update_data = {"is_superuser": False}
            case Role.superuser:
                update_data = {"is_superuser": True}
            case _:
                assert_never(role)
        return await self.uow.users.update(user_id, **update_data)
