import time

from aiogram import types, Dispatcher
from create_bot import bot
from aiogram.dispatcher.filters import Text
from keyboards import kb_markup_main, location_markup, my_retailers_delete_add
from database import insert_new_user, create_bug_report, add_retailer_to_user_list, \
    select_retailers_name_added_by_user, delete_retailer_added_by_user, select_primitive_algorithm, \
    look_for_prices_in_added_retailers
from functions import available_retailers_keyboard, users_retailers_keyboard
from asyncio import sleep


async def start_help(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, text=f'Привет, {message.from_user.first_name}! '
                                                          f'Это чат-бот «Купи дешевле».\n\nЯ сравниваю цены на товары '
                                                          f'ваших любимых производителей. Со мной можно сэкономить '
                                                          f'более 30% от стоимости товара.')
        await insert_new_user(message.from_user.id)
        await sleep(3)
        await bot.send_message(message.from_user.id, text="Мне нужно знать ваш адрес, чтобы не рекомендовать товары, "
                                                          "которых нет в магазинах рядом с вами")
        await sleep(1)
        await bot.send_message(message.from_user.id, text='Нажмите на кнопку "Поделиться местоположением"',
                               reply_markup=location_markup)
        await sleep(2)
        # await message.delete()
    except Exception as ex:
        print(ex)
        await message.reply("Что-то пошло не так...")


async def search_and_add_retailers(message: types.Message):
    await bot.send_message(message.from_user.id, "Ищем ближайшие магазины", reply_markup=kb_markup_main)
    await sleep(2)

    msg = "Вот что удалось найти. Отметьте супермаркеты, которые вы посещаете"
    kb = await available_retailers_keyboard()
    await bot.send_message(message.from_user.id, text=msg, reply_markup=kb)


async def add_retailer_by_name_to_the_list(callback: types.CallbackQuery):
    retailer_id = int(callback.data.split()[2])
    if retailer_id > 0:
        result = await add_retailer_to_user_list(callback.from_user.id, retailer_id)
        await callback.answer(result, show_alert=True)
    else:
        users_retailers_tuple = await select_retailers_name_added_by_user(callback.from_user.id)
        if len(users_retailers_tuple) == 0:
            await bot.send_message(callback.from_user.id, "Укажите хотя бы один магазин, чтобы я знал, где "
                                                          "искать")
        else:
            await bot.send_message(callback.from_user.id, "Отлично! Теперь я готов искать цены на ваши любимые "
                                                          "товары!")
            await sleep(1)
            await bot.send_message(callback.from_user.id, "Я пока знаю цены только на эти категории товаров:\n"
                                                          "1. Стиральные порошки\n2. Шампуни\n3. Подгузники")
            await sleep(1.5)
            await bot.send_message(callback.from_user.id,
                                   'Введите запрос в формате:\n"Порошок стиральный Losk Color 2,7 кг"',
                                   reply_markup=kb_markup_main)


# async def my_list(message: types.Message):
# await bot.send_message(message.from_user.id, 'Раздел ещё находится в разработке')
# создать новый если из бд ничего не вернулось, на кнопках вывести существующие
# выводить кнопку после каждого высланного товара "добавить в список"


async def my_retailers(message: types.Message):
    users_retailers_tuple = await select_retailers_name_added_by_user(telegram_id=message.from_user.id)
    if len(users_retailers_tuple) == 0:
        await bot.send_message(message.from_user.id, text="В списке нет ни одного магазина")
        await sleep(1.5)
        msg = "Отметьте супермаркеты, которые вы посещаете"
        kb = await available_retailers_keyboard()
        await bot.send_message(message.from_user.id, text=msg, reply_markup=kb)
    else:
        result = ""
        for retailer in users_retailers_tuple:
            result += f'{retailer[1]}\n'
        result.rstrip(" ")
        await bot.send_message(message.from_user.id, result)
        await bot.send_message(message.from_user.id, text="Что вы хотите сделать?",
                               reply_markup=my_retailers_delete_add)


async def delete_retailer_from_user_list_message(callback: types.CallbackQuery):
    kb = await users_retailers_keyboard(callback.from_user.id)
    await bot.send_message(callback.from_user.id,
                           text="Какой магазин вы хотите удалить?",
                           reply_markup=kb)


async def remove_retailer_from_user_list(callback: types.CallbackQuery):
    retailer_id = int(callback.data.split()[2])
    if retailer_id > 0:
        result = await delete_retailer_added_by_user(callback.from_user.id, retailer_id)
        if not result:
            await callback.answer("Магазин уже удалён либо не был добавлен прежде", show_alert=True)
        else:
            await callback.answer("Изменения сохранены", show_alert=True)
    else:
        users_retailers_tuple = await select_retailers_name_added_by_user(telegram_id=callback.from_user.id)
        if len(users_retailers_tuple) == 0:
            await bot.send_message(callback.from_user.id, text="В списке нет ни одного магазина")
            await sleep(1.5)
            msg = "Отметьте супермаркеты, которые вы посещаете"
            kb = await available_retailers_keyboard()
            await bot.send_message(callback.from_user.id, text=msg, reply_markup=kb)
        else:
            await bot.send_message(callback.from_user.id, text='Изменения сохранены. Можете продолжать поиск цен\n\n '
                                                               'Введите запрос в формате:\n'
                                                               '"Порошок стиральный Losk Color 2,7 кг"')


# если нет магазинов в списке - не искать
async def known_category(message: types.Message):
    query = str(message.text).rstrip()
    tuple_from_database = await select_primitive_algorithm(query)
    if len(tuple_from_database) == 0:
        await bot.send_message(message.from_user.id, text="Я пока не знаю цены на данный товар.\n\nУточните запрос в "
                                                          "соответствии с требуемым форматом или найдите другой товар")
    elif len(tuple_from_database) == 1:
        product_id = tuple_from_database[0][0]
        retailer_name_and_price = await look_for_prices_in_added_retailers(message.from_user.id, product_id)
        response = ""
        for el in retailer_name_and_price:
            response += el[0] + " - " + str(el[1]) + " руб" + "\n"
        await bot.send_message(message.from_user.id, text=response.rstrip())
    else:
        await bot.send_message(message.from_user.id, text="Я знаю цены на товары из этого списка:\n\n")


async def echo_send(message: types.Message):
    await bot.send_message(message.from_user.id, "Эта категория пока недоступна для поиска")


async def bug(message: types.Message):
    await bot.send_message(message.from_user.id, 'Опишите проблему, с которой столкнулись, в формате "Ошибка: '
                                                 '[ваш текст]".')


async def bug_report(message: types.Message):
    report = str(message.text).replace(":", "", 1)
    print(report)
    await create_bug_report(report)
    await bot.send_message(message.from_user.id, 'Спасибо, что помогаете '
                                                 'развивать чат-бот!')
    time.sleep(1)
    await bot.send_message(message.from_user.id, 'Введите запрос в формате:\n"Порошок стиральный Losk Color 2,7 кг"',
                           reply_markup=kb_markup_main)


def message_handlers(dp: Dispatcher):
    dp.register_message_handler(start_help, commands=['start', 'help'])
    dp.register_message_handler(search_and_add_retailers, content_types=['location'])
    dp.register_message_handler(search_and_add_retailers, Text(equals="Поделиться местоположением"))
    dp.register_callback_query_handler(search_and_add_retailers, Text(equals="Добавить магазин"))
    dp.register_callback_query_handler(add_retailer_by_name_to_the_list, Text(startswith="add retailer"))
    dp.register_message_handler(my_retailers, lambda message: "ои магазины" in message.text)
    dp.register_callback_query_handler(delete_retailer_from_user_list_message,
                                       Text(equals='Удалить магазин', ignore_case=True))
    dp.register_callback_query_handler(remove_retailer_from_user_list, Text(startswith="remove retailer"))
    dp.register_message_handler(bug, Text(equals='Сообщить об ошибке', ignore_case=True))
    dp.register_message_handler(bug_report, lambda message: "шибка" in message.text)
    # dp.register_message_handler(known_category, lambda message: "орошок" in str(message.text).split(" ")[0] or
    # "одгузники" in str(message.text).split(" ")[0] or
    # "ампунь" in str(message.text).split(" ")[0])
    dp.register_message_handler(known_category, lambda message: str(message).count(" ") >= 1)
    # dp.register_message_handler(my_list, lambda message: "писки" in message.text)

    dp.register_message_handler(echo_send)
