from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import ADDRESS_TEXT, BOOKING_URL, GROUP_ID, PHONE_TEXT, SITE_URL, TELEGRAM_CONTACT
from db import NamePhoto
from services.bot_messages import send_message_with_auto_delete
from services.spa_parser import SpaParser


def build_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='Сайт', url=SITE_URL)
    kb.button(text='Запись', url=BOOKING_URL)
    kb.adjust(1)
    return kb.as_markup()


def build_today_caption(masters: list[NamePhoto]) -> str:
    master_lines = ''.join(f'⭐️ {master.name}\n\n' for master in masters)
    return (
        '<b>💟 МАСТЕРА СЕГОДНЯ:</b>\n'
        f'{master_lines}'
        f'📍 {ADDRESS_TEXT}\n'
        f'❤️ {TELEGRAM_CONTACT}\n'
        f'Тел. {PHONE_TEXT}'
    )


async def refresh_today_masters() -> list[NamePhoto]:
    parser = SpaParser()
    masters = parser.fetch_today_masters()

    await NamePhoto.all().delete()
    for master in masters:
        await NamePhoto.create(name=master.html_link, list_photo=master.photos)

    return await NamePhoto.all()


async def publish_today_masters(bot: Bot, chat_id: int | str = GROUP_ID, scheduler: AsyncIOScheduler | None = None):
    masters = await refresh_today_masters()
    caption = build_today_caption(masters)

    return await send_message_with_auto_delete(
        bot=bot,
        chat_id=chat_id,
        text=caption,
        scheduler=scheduler,
        disable_web_page_preview=True,
        reply_markup=build_main_keyboard(),
    )
