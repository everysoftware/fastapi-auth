from app.core.uow import UOW


class UnauthorizedGateway:
    """
    Provides access to application core without authentication.
    """

    def __init__(self, uow: UOW):
        self.uow = uow


class Gateway(UnauthorizedGateway):
    """
    Provides access to application core.

    e.g.::

        async def get_user(
            email: str, gateway: Annotated[ServiceGateway, Depends(get_gateway)]
        ) -> None:
            user = await gateway.users.get_by_email(str)
            return user


        async def handler(message: types.Message, gateway: ServiceGateway) -> None:
            user = await gateway.users.get_by_email(message.text)
            await message.answer(user.model_dump_json())
    """  # noqa: E501

    # User info
    # ...

    # Infrastructure
    # ...

    # Services
    # ...

    def __init__(self, uow: UOW):
        super().__init__(uow)
