import asyncio
import logging
import os

import django
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from bot.config import TG_BOT_TOKEN
from bot.routers.start import router as start_router
from bot.routers.catalog import router as catalog_router
from bot.routers.orders import router as orders_router
from bot.routers.upload import router as upload_router
from bot.routers.admin import router as admin_router
from bot.routers.support import router as support_router


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    for router in (start_router, catalog_router, orders_router, upload_router, admin_router, support_router):
        dp.include_router(router)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
