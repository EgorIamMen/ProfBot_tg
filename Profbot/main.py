import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers.quiz import quiz_router
from handlers.start import start_router
from db.db import init_db

CODE_VERSION = "v3 - 2025-09-11"

bot = Bot(token=TOKEN)
dp = Dispatcher()


dp.include_router(start_router)
dp.include_router(quiz_router)


async def main():
    await init_db()
    print(f"🚀 Запускаю бота, версия {CODE_VERSION}")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
