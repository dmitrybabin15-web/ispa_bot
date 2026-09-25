import logging

from aiogram import Router, types

from data.config import ADMIN_IDS
from services.bot_messages import send_message_with_auto_delete
from services.publishing import publish_today_masters

logger = logging.getLogger(__name__)
router = Router()


@router.message()
async def handle_admin_publish_request(message: types.Message) -> None:
    if message.from_user is None or message.from_user.id not in ADMIN_IDS:
        return

    await send_message_with_auto_delete(
        bot=message.bot,
        chat_id=message.chat.id,
        text='Обновляю список мастеров и публикую сообщение...',
    )

    try:
        await publish_today_masters(bot=message.bot, chat_id=message.chat.id)
    except Exception:
        logger.exception('Could not publish today masters')
        await send_message_with_auto_delete(
            bot=message.bot,
            chat_id=message.chat.id,
            text='Не получилось обновить и опубликовать список мастеров. Проверь логи.',
        )
