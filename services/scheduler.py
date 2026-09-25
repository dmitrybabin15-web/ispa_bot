import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import DAILY_PUBLICATION_HOUR, DAILY_PUBLICATION_MINUTE, TIMEZONE
from services.bot_messages import delete_expired_bot_messages, restore_pending_deletion_jobs
from services.publishing import publish_today_masters

logger = logging.getLogger(__name__)


async def start_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    scheduler.add_job(
        publish_today_masters,
        trigger='cron',
        hour=DAILY_PUBLICATION_HOUR,
        minute=DAILY_PUBLICATION_MINUTE,
        args=[bot],
        kwargs={'scheduler': scheduler},
        id='publish_today_masters',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.add_job(
        delete_expired_bot_messages,
        trigger='interval',
        seconds=60,
        args=[bot],
        id='delete_expired_bot_messages',
        replace_existing=True,
    )

    scheduler.start()
    await restore_pending_deletion_jobs(scheduler, bot)
    logger.info('Scheduler started')
    return scheduler
