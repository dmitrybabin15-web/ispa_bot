import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import BOT_MESSAGE_TTL_SECONDS
from db import BotMessage

logger = logging.getLogger(__name__)


def get_delete_at() -> datetime:
    return datetime.now() + timedelta(seconds=BOT_MESSAGE_TTL_SECONDS)


async def remember_bot_message(message: Message, delete_at: datetime) -> None:
    await BotMessage.create(
        chat_id=message.chat.id,
        message_id=message.message_id,
        delete_at=delete_at,
    )


async def send_message_with_auto_delete(
    bot: Bot,
    chat_id: int | str,
    text: str,
    scheduler: AsyncIOScheduler | None = None,
    **kwargs: Any,
) -> Message:
    message = await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    delete_at = get_delete_at()
    await remember_bot_message(message, delete_at)

    if scheduler is not None:
        schedule_message_deletion(scheduler, bot, message.chat.id, message.message_id, delete_at)
    else:
        asyncio.create_task(delete_bot_message_later(bot, message.chat.id, message.message_id, delete_at))

    return message


def schedule_message_deletion(
    scheduler: AsyncIOScheduler,
    bot: Bot,
    chat_id: int,
    message_id: int,
    run_at: datetime,
) -> None:
    scheduler.add_job(
        delete_bot_message,
        trigger='date',
        run_date=run_at,
        args=[bot, chat_id, message_id],
        id=f'delete_bot_message:{chat_id}:{message_id}',
        replace_existing=True,
        misfire_grace_time=3600,
    )


async def delete_bot_message_later(bot: Bot, chat_id: int, message_id: int, delete_at: datetime) -> None:
    delay_seconds = max(0, (delete_at - datetime.now()).total_seconds())
    await asyncio.sleep(delay_seconds)
    await delete_bot_message(bot, chat_id, message_id)


async def delete_bot_message(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as err:
        logger.warning('Could not delete bot message %s/%s: %s', chat_id, message_id, err)
    finally:
        await BotMessage.filter(chat_id=chat_id, message_id=message_id).delete()


async def delete_expired_bot_messages(bot: Bot) -> None:
    messages = await BotMessage.filter(delete_at__lte=datetime.now()).all()
    for message in messages:
        await delete_bot_message(bot, message.chat_id, message.message_id)


async def restore_pending_deletion_jobs(scheduler: AsyncIOScheduler, bot: Bot) -> None:
    now = datetime.now()
    pending_messages = await BotMessage.filter(delete_at__gt=now).all()
    for message in pending_messages:
        schedule_message_deletion(
            scheduler=scheduler,
            bot=bot,
            chat_id=message.chat_id,
            message_id=message.message_id,
            run_at=message.delete_at,
        )
