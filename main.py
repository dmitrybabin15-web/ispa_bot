import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import handlers
from data.config import BOT_TOKEN
from db import init, on_shutdown
from services.scheduler import start_scheduler
from utils.logging_setup import setup_logging

setup_logging(logs_dir="logs", level=logging.INFO)


def register_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(handlers.router)


def init_bot() -> Bot:
    return Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


async def main() -> None:
    bot = init_bot()
    dispatcher = Dispatcher()
    register_routers(dispatcher)

    await init()
    scheduler = await start_scheduler(bot)

    try:
        logging.info('Bot started')
        await dispatcher.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await on_shutdown()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
