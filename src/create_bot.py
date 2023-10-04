from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configparser


config = configparser.ConfigParser()
config.read("secrets.ini")

storage = MemoryStorage()


token = config["Server"]["API_TOKEN"][1:-1]

bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)
