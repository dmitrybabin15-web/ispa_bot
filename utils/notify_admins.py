import logging

from aiogram import Bot

from data.config import ADMIN_IDS
from services.bot_messages import send_message_with_auto_delete

logger = logging.getLogger(__name__)


async def on_startup_notify(bot: Bot) -> None:
    for admin_id in ADMIN_IDS:
        try:
            await send_message_with_auto_delete(bot=bot, chat_id=admin_id, text='Бот запущен')
        except Exception as err:
            logger.exception('Could not notify admin %s: %s', admin_id, err)
