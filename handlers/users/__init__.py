from aiogram import Router

from .start import router as start_router

router = Router(name=__name__)
router.include_router(start_router)
