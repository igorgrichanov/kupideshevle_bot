from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()


API_TOKEN = "5230145407:AAE2UixUInuiOObYZf6SH76ZrxpYlflwCrw"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
