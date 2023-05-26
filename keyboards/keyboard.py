from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


b1 = KeyboardButton("Мои списки")
b2 = KeyboardButton("Мои магазины")
b3 = KeyboardButton("Сообщить об ошибке")

kb_markup_main = ReplyKeyboardMarkup(resize_keyboard=True)
kb_markup_main.row(b1, b2, b3)

my_retailers_delete_add = InlineKeyboardMarkup(row_width=2)
my_retailers_markup_b1 = InlineKeyboardButton(text="Удалить магазин", callback_data="Удалить магазин")
my_retailers_markup_b2 = InlineKeyboardButton(text="Добавить магазин", callback_data="Добавить магазин")
my_retailers_delete_add.row(my_retailers_markup_b1, my_retailers_markup_b2)

location_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
location_button = KeyboardButton("Поделиться местоположением", request_location=True)
location_markup.add(location_button)

add_product_to_list = InlineKeyboardMarkup()
add_product_to_list_button = InlineKeyboardButton(text="Добавить в список", callback_data="add to list")
add_product_to_list.add(add_product_to_list_button)

add_new_product_list = InlineKeyboardMarkup()
add_new_product_list_button = InlineKeyboardButton(text="Создать новый список", callback_data="create new list")
add_new_product_list.add(add_new_product_list_button)


async def create_inline_kb(buttons: int):
    kb = InlineKeyboardMarkup(row_width=buttons)
    return kb
