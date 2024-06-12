from fastabc import AlchemyUOW


class UOW(AlchemyUOW):
    async def on_open(self) -> None:
        pass
