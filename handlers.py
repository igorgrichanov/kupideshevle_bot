import time

from aiogram import types, Dispatcher
from create_bot import bot
from aiogram.dispatcher.filters import Text
from keyboards import kb_markup_main, location_markup, my_retailers_delete_add, add_product_to_list, add_new_product_list
from database import insert_new_user, create_bug_report, add_retailer_to_user_list, \
    select_retailers_added_by_user, delete_retailer_added_by_user, select_primitive_algorithm, user_product_list, \
    add_new_product_list_query
from functions import available_retailers_keyboard, users_retailers_keyboard, found_goods_keyboard
from asyncio import sleep


async def locate(message: types.Message):
    await bot.send_message(message.from_user.id, text="Давайте найдём ближайшие магазины, чтобы сравнить цены в них")
    await sleep(1)
    await bot.send_message(message.from_user.id, text='Нажмите на кнопку "Поделиться местоположением"',
                           reply_markup=location_markup)


async def start_help(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, text=f'Привет, {message.from_user.first_name}! '
                                                          f'Это чат-бот «Купи дешевле».\n\nЯ сравниваю цены на товары '
                                                          f'ваших любимых производителей. Со мной можно сэкономить '
                                                          f'более 30% от стоимости товара.')
        await insert_new_user(message.from_user.id)
        await sleep(3)
        await locate(message)

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
        users_retailers_tuple = await select_retailers_added_by_user(callback.from_user.id)
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


async def my_product_list(message: types.Message):
    lists = await user_product_list(message.from_user.id)
    if len(lists) == 0:
        await bot.send_message(message.from_user.id, "У вас пока нет ни одного списка",
                               reply_markup=add_new_product_list)
    else:
        msg = ""
        for list_name in lists:
            msg += f'{list_name[0]}\n'
        msg.rstrip(" ")
        await bot.send_message(message.from_user.id, msg, reply_markup=add_new_product_list)
# создать новый если из бд ничего не вернулось, на кнопках вывести существующие
# выводить кнопку после каждого высланного товара "добавить в список"


async def insert_new_product_list(message: types.Message):
    await bot.send_message(message.from_user.id, "Чтобы создать новый список, отправьте его название со знаком \"!\" "
                                                 "в начале.\n\nПример: !Частое")


async def add_new_list_by_name_handler(message: types.Message):
    list_name = message.text.lstrip("!").lstrip(" ")
    result = await add_new_product_list_query(message.from_user.id, list_name)
    if result != "":
        await bot.send_message(message.from_user.id, result)
    else:
        await bot.send_message(message.from_user.id, "Список успешно создан!")


async def my_retailers(message: types.Message):
    users_retailers_tuple = await select_retailers_added_by_user(telegram_id=message.from_user.id)
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
        users_retailers_tuple = await select_retailers_added_by_user(telegram_id=callback.from_user.id)
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


async def look_for_price(message: types.Message):
    users_retailers_tuple = await select_retailers_added_by_user(telegram_id=message.from_user.id)
    if len(users_retailers_tuple) == 0:
        await bot.send_message(message.from_user.id, text="В списке нет ни одного магазина")
        await sleep(1.5)
        msg = "Отметьте супермаркеты, которые вы посещаете"
        kb = await available_retailers_keyboard()
        await bot.send_message(message.from_user.id, text=msg, reply_markup=kb)
    else:
        query = str(message.text).rstrip()
        tuple_from_database = await select_primitive_algorithm(query, message.from_user.id)
        if len(tuple_from_database) == 0:
            await bot.send_message(message.from_user.id, text="Я пока не знаю цены на данную категорию.\n\nПопробуйте "
                                                              "уточнить запрос в соответствии с требуемым форматом или "
                                                              "найти другой товар")
        else:
            if len(tuple_from_database) <= len(await select_retailers_added_by_user(message.from_user.id)):
                msg = ""
                for info in tuple_from_database:
                    msg += f'{info[1]} - {info[2]} руб.\n'
                msg.rstrip(" ")
                await bot.send_message(message.from_user.id, text=msg, reply_markup=add_product_to_list)
            else:
                await bot.send_message(message.from_user.id, text="Были найдены цены на следующие товары. Если в этом "
                                                                  "списке есть тот, который вас интересует - отправьте "
                                                                  "его в чат, чтобы узнать цены")
                await sleep(2)

                kb, msg = await found_goods_keyboard(tuple_from_database)
                await bot.send_message(message.from_user.id, text=msg, reply_markup=kb)


async def look_for_concrete_good(callback: types.CallbackQuery):
    query = str(callback.data)
    query = query[query.find(" ") + 1:].rstrip(" ")
    tuple_from_database = await select_primitive_algorithm(query, callback.from_user.id)
    msg = ""
    for info in tuple_from_database:
        msg += f'{info[1]} - {info[2]} руб.\n'
    msg.rstrip(" ")
    await bot.send_message(callback.from_user.id, text=msg, reply_markup=add_product_to_list)


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
    dp.register_callback_query_handler(locate, Text(equals="Добавить магазин"))
    dp.register_callback_query_handler(add_retailer_by_name_to_the_list, Text(startswith="add retailer"))
    dp.register_message_handler(my_retailers, lambda message: "ои магазины" in message.text)
    dp.register_callback_query_handler(delete_retailer_from_user_list_message,
                                       Text(equals='Удалить магазин', ignore_case=True))
    dp.register_callback_query_handler(remove_retailer_from_user_list, Text(startswith="remove retailer"))
    dp.register_message_handler(my_product_list, Text(equals="Мои списки"))
    dp.register_callback_query_handler(insert_new_product_list, Text(equals="create new list"))
    dp.register_message_handler(add_new_list_by_name_handler, Text(startswith="!"))
    dp.register_message_handler(bug, Text(equals='Сообщить об ошибке', ignore_case=True))
    dp.register_message_handler(bug_report, lambda message: "шибка" in message.text)
    dp.register_callback_query_handler(look_for_concrete_good, Text(startswith="lf"))
    dp.register_message_handler(look_for_price)
