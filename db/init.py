import os

from tortoise import Tortoise


async def init() -> None:
    db_url = os.getenv('DB_URL') or f"sqlite://{os.getenv('DB_FILE', 'db.sqlite3')}"
    await Tortoise.init(db_url=db_url, modules={'models': ['db.models']})
    await Tortoise.generate_schemas(safe=True)


async def on_shutdown() -> None:
    await Tortoise.close_connections()
