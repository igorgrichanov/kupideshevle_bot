from aiogram import executor
from src.create_bot import dp
from src.handlers import message_handlers


async def on_startup(_):
    print("Online")


message_handlers(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
