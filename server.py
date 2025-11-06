
import asyncio
import logging
import os  
from dotenv import load_dotenv  

from aiogram import Bot, Dispatcher
from app.handlers import router
from app.data_manager import load_all_item_data


load_dotenv()
API_KEY = os.getenv("STEAM_API_KEY")


logging.basicConfig(level=logging.INFO)


if not API_KEY:
    logging.critical("STEAM_API_KEY не найден! Убедись, что .env файл существует и содержит ключ.")
    exit() 
else:
    logging.info("STEAM_API_KEY успешно загружен.")


dp = Dispatcher()

async def main() -> None:
    bot = Bot(token="your token here")

    dp.include_router(router)

    await load_all_item_data()
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ =='__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt):
       print('Bot stopped')
