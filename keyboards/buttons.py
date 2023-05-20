from aiogram.types import InlineKeyboardButton


async def create_inline_button(text, callback):
    button = InlineKeyboardButton(text=text, callback_data=callback)
    return button
