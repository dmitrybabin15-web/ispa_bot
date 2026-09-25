from .users import router as user_router
from aiogram import Router


router = Router(name=__name__)


router.include_router(user_router)
