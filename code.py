from aiogram import executor
from create_bot import dp
from handlers import message_handlers


async def on_startup(_):
    print("Online1")


message_handlers(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
