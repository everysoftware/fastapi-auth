import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.logging import logger
from app.telegram.bot import bot as tg_bot
from app.telegram.start import router as start_router

routers = [start_router]


async def on_startup(bot: Bot, dispatcher: Dispatcher) -> None:
    pass


async def on_shutdown(bot: Bot, dispatcher: Dispatcher) -> None:
    pass


dp = Dispatcher()
dp.include_routers(*routers)
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


def start_polling() -> None:
    """
    Start polling the bot. Supports graceful shutdown.
    Use this instead of `asyncio.run(dp.start_polling(bot))` to support graceful shutdown
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling(tg_bot))


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    start_polling()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
