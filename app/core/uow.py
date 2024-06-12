from onepattern import AlchemyUOW


class UOW(AlchemyUOW):
    # Repositories
    # ...
    async def on_open(self) -> None:
        # self.users = UserRepository(self.session)
        # ...
        pass
