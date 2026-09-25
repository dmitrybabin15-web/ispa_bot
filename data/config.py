import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name, '').strip()
    if not value:
        raise RuntimeError(f'{name} is empty. Set it in environment or .env')
    return value


def get_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name, '').strip()
    if not raw_value:
        return default
    return int(raw_value)


def get_int_list_env(name: str, default: list[int]) -> list[int]:
    raw_value = os.getenv(name, '').strip()
    if not raw_value:
        return default
    return [int(item.strip()) for item in raw_value.split(',') if item.strip()]


BOT_TOKEN = get_required_env('BOT_TOKEN')
GROUP_ID = get_int_env('GROUP_ID', -1002948213273)
ADMIN_IDS = get_int_list_env('ADMIN_IDS', [6068353947])
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow').strip() or 'Europe/Moscow'

DAILY_PUBLICATION_HOUR = get_int_env('DAILY_PUBLICATION_HOUR', 11)
DAILY_PUBLICATION_MINUTE = get_int_env('DAILY_PUBLICATION_MINUTE', 30)
BOT_MESSAGE_TTL_SECONDS = get_int_env('BOT_MESSAGE_TTL_SECONDS', 23 * 60 * 60 + 59 * 60 + 59)

SITE_URL = os.getenv('SITE_URL', 'https://i-spa.su/girls/').strip()
BOOKING_URL = os.getenv('BOOKING_URL', 'https://t.me/spa_spb78').strip()
ADDRESS_TEXT = os.getenv('ADDRESS_TEXT', 'СПБ. ул.Театральная пл. дом 8').strip()
TELEGRAM_CONTACT = os.getenv('TELEGRAM_CONTACT', '@spa_spb78').strip()
PHONE_TEXT = os.getenv('PHONE_TEXT', '+7-931-393-33-68').strip()
