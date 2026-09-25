"""
Telegram бот с webhook вместо polling.
Развёртывание на Beget VPS.
Использует aiohttp для корректной асинхронности.
"""

import asyncio
import logging
from typing import Optional

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

import handlers
from data.config import BOT_TOKEN
from db import init, on_shutdown as db_on_shutdown
from services.scheduler import start_scheduler
from utils.logging_setup import setup_logging

# Логирование (и в stdout, и в файлы с ротацией)
setup_logging(logs_dir="logs", level=logging.INFO)
logger = logging.getLogger(__name__)


class BotConfig:
    """Конфигурация бота."""
    
    BOT_TOKEN = BOT_TOKEN
    WEBHOOK_PATH = '/webhook'
    WEBHOOK_HOST = '0.0.0.0'
    WEBHOOK_PORT = 8000


class BotInstance:
    """Синглтон для хранения состояния бота."""
    
    bot: Optional[Bot] = None
    dispatcher: Optional[Dispatcher] = None
    scheduler = None


async def on_startup(app: web.Application) -> None:
    """Инициализация при запуске приложения."""
    logger.info("Initializing bot...")
    
    # Создаём бота и диспетчер
    BotInstance.bot = Bot(
        BotConfig.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    BotInstance.dispatcher = Dispatcher()
    
    # Регистрируем обработчики
    BotInstance.dispatcher.include_router(handlers.router)
    
    # Инициализируем БД
    await init()
    
    # Запускаем планировщик
    BotInstance.scheduler = await start_scheduler(BotInstance.bot)
    
    logger.info("Bot initialized successfully")


async def on_shutdown(app: web.Application) -> None:
    """Очистка при остановке приложения."""
    logger.info("Shutting down bot...")
    
    if BotInstance.scheduler:
        BotInstance.scheduler.shutdown(wait=False)
    
    await db_on_shutdown()
    
    if BotInstance.bot:
        await BotInstance.bot.session.close()
    
    logger.info("Bot shutdown completed")


async def webhook_handler(request: web.Request) -> web.Response:
    """
    Обработчик webhook от Telegram.
    POST /webhook - получает обновления от Telegram.
    """
    if BotInstance.bot is None or BotInstance.dispatcher is None:
        logger.error("Bot not initialized")
        return web.Response(status=503, text="Server not ready")
    
    try:
        update_data = await request.json()
        
        # Преобразуем JSON в объект Update
        update = Update(**update_data)
        
        # Передаём обновление в диспетчер
        await BotInstance.dispatcher.feed_update(BotInstance.bot, update)
        
        return web.Response(status=200, text="ok")
    
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return web.Response(status=500, text=f"Error: {str(e)}")


async def health_handler(request: web.Request) -> web.Response:
    """Проверка здоровья приложения."""
    if BotInstance.bot is None:
        return web.Response(status=503, text="Not ready")
    return web.Response(status=200, text="ok")


async def index_handler(request: web.Request) -> web.Response:
    """Главная страница."""
    return web.Response(
        status=200,
        text="Telegram Bot API (Webhook)",
        content_type="text/plain"
    )


def create_app() -> web.Application:
    """Создаёт и настраивает aiohttp приложение."""
    app = web.Application()
    
    # Регистрируем сигналы
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_shutdown)
    
    # Регистрируем маршруты
    app.router.add_post(BotConfig.WEBHOOK_PATH, webhook_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/', index_handler)
    
    return app


if __name__ == '__main__':
    # Для локального запуска: python main_webhook.py
    # Для production: gunicorn --worker-class aiohttp.GunicornWebWorker --bind 0.0.0.0:8000 main_webhook:create_app
    
    app = create_app()
    web.run_app(app, host=BotConfig.WEBHOOK_HOST, port=BotConfig.WEBHOOK_PORT)
