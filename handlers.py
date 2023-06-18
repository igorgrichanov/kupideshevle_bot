from aiogram import types, Dispatcher
from create_bot import bot
from aiogram.dispatcher.filters import Text
from keyboards import kb_markup_main, location_markup, my_retailers_delete_add
from keyboards import available_retailers_keyboard, users_retailers_keyboard, concrete_list_actions, \
    user_product_lists_keyboard, remove_product_from_list_keyboard
from database import insert_new_user, create_bug_report, add_retailer_to_user_list, \
    select_retailers_added_by_user, delete_retailer_added_by_user, add_new_product_list_query, \
    add_product_to_user_list, product_list_content, rename_product_list_query, \
    remove_product_from_list_query, delete_list_by_name_query
from functions import look_for_price, look_for_concrete_good
from asyncio import sleep
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


async def locate(message: types.Message):
    await bot.send_message(message.from_user.id, text="Давайте найдём ближайшие магазины, чтобы сравнить цены в них")
    await sleep(1)
    await bot.send_message(message.from_user.id, text='Нажмите на кнопку "Поделиться местоположением"',
                           reply_markup=location_markup)


async def start_help(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, text=f'Привет, {message.from_user.first_name}! '
                                                          f'Это чат-бот <b>«Купи дешевле»</b>.\n\n'
                                                          f'Я сравниваю цены на товары ваших любимых производителей. '
                                                          f'Со мной можно сэкономить <b>более 30%</b> от стоимости '
                                                          f'товара.', parse_mode=types.ParseMode.HTML)
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
            await bot.send_message(callback.from_user.id, "Цены во всех магазинах доступны только на эти категории "
                                                          "товаров:\n1. Стиральные порошки\n2. Шампуни\n"
                                                          "3. Подгузники\n\nМожете найти и другие товары, "
                                                          "но цены на них пока доступны не во всех магазинах")
            await sleep(1.5)
            await bot.send_message(callback.from_user.id,
                                   'Отправьте название товара, который хотите найти.\nНапример, <i>Шампунь Schauma</i>'
                                   ' или <i>Подгузники</i>',
                                   reply_markup=kb_markup_main, parse_mode=types.ParseMode.HTML)


async def my_product_lists(message: types.Message):
    kb, flag = await user_product_lists_keyboard(message.from_user.id)
    if flag:
        await bot.send_message(message.from_user.id, "Чтобы просмотреть, изменить или удалить список - нажмите на "
                                                     "кнопку с его названием", reply_markup=kb)
    else:
        await bot.send_message(message.from_user.id, "У вас пока нет ни одного списка. Нажмите на эту кнопку, чтобы "
                                                     "создать ваш первый список продуктов", reply_markup=kb)


class FSMForUserLists(StatesGroup):
    name = State()


async def insert_new_product_list(callback: types.CallbackQuery):
    await FSMForUserLists.name.set()
    await sleep(1)
    await bot.send_message(callback.from_user.id, text="Отправьте имя нового списка")


async def add_new_list_by_name_handler(message: types.Message, state: FSMContext):
    list_name = message.text
    if list_name == "-":
        await state.finish()
        await bot.send_message(message.from_user.id, "Я готов работать дальше!")
    elif list_name != "Мои списки" and list_name != "Мои магазины" and list_name != "Сообщить об ошибке":
        result = await add_new_product_list_query(message.from_user.id, message.text)
        if result != "":
            await bot.send_message(message.from_user.id, result)
        else:
            await bot.send_message(message.from_user.id, "Список успешно создан!\n\nКстати, вы можете добавить ранее "
                                                         "найденные товары в только что созданный список. "
                                                         "Для этого нужно пролистать выше до результатов поиска и "
                                                         "снова нажать на кнопку с номером товара")
            await state.finish()
    else:
        await bot.send_message(message.from_user.id, 'Если вы передумали создавать список, отправьте знак "-"')


async def print_list_content(callback: types.CallbackQuery):
    list_id, list_name = int(callback.data.split(" ")[1]), callback.data.split(" ")[2]
    list_content, exists = await product_list_content(list_id=list_id)
    if len(list_content) != 0:
        msg = f"Содержимое списка <b>{list_name}</b>\n\n"
        i = 1
        for product in list_content:
            msg += f'{i}. {product[1]}\n'
            i += 1
        msg.rstrip()
        kb = await concrete_list_actions(False, list_id, list_name)
        await bot.send_message(callback.from_user.id, text=msg, reply_markup=kb, parse_mode=types.ParseMode.HTML)
    elif exists:
        kb = await concrete_list_actions(True, list_id, list_name)
        msg = 'Список пуст. Чтобы добавить товар в список, отправьте название товара, который хотите найти.\n' \
              'Например, <i>Шампунь Schauma"</i> или <i>Подгузники</i>'
        await bot.send_message(callback.from_user.id, text=msg, reply_markup=kb, parse_mode=types.ParseMode.HTML)
    else:
        msg = "Такого списка больше не существует. Выберите другой или создайте новый"
        await bot.send_message(callback.from_user.id, text=msg)


class FSMForRenameList(StatesGroup):
    newName = State()


async def rename_product_list_handler(callback: types.CallbackQuery):
    await FSMForRenameList.newName.set()
    list_name_lst = callback.data.split()[2:]
    list_name = " ".join(list_name_lst)
    await sleep(1)
    await bot.send_message(callback.from_user.id, text=f"Отправьте новое имя списка {list_name} в формате:\n\n"
                                                       f"Старое имя - новое имя")


async def rename_product_list(message: types.Message, state: FSMContext):
    new_list_name = str(message.text[message.text.find("-") + 1:]).lstrip()
    old_list_name = str(message.text[:message.text.find("-")]).rstrip()
    result = await rename_product_list_query(old_list_name, new_list_name, message.from_user.id)
    await bot.send_message(message.from_user.id, result)
    await state.finish()


async def remove_product_from_list_handler(callback: types.CallbackQuery):
    list_id = int(callback.data.split()[3])
    kb = await remove_product_from_list_keyboard(list_id)
    await bot.send_message(callback.from_user.id, "Нажмите на кнопку с номером товара, который требуется удалить",
                           reply_markup=kb)


async def remove_product_from_list(callback: types.CallbackQuery):
    product_id = int(callback.data.split()[2])
    list_id = int(callback.data.split()[3])
    result = await remove_product_from_list_query(list_id, product_id)
    await callback.answer(result, show_alert=True)


async def delete_list_by_name_handler(callback: types.CallbackQuery):
    list_id = int(callback.data.split()[2])
    result = await delete_list_by_name_query(list_id)
    await callback.answer(result, show_alert=True)


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
                                                               'Отправьте название товара, который хотите найти.\n'
                                                               'Например, <i>Шампунь Schauma"</i> или '
                                                               '<i>Подгузники Huggies</i>',
                                   parse_mode=types.ParseMode.HTML)


async def look_for_price_handler(message: types.Message):
    users_retailers_tuple = await select_retailers_added_by_user(telegram_id=message.from_user.id)
    if len(users_retailers_tuple) == 0:
        await bot.send_message(message.from_user.id, text="В списке нет ни одного магазина")
        await sleep(1.5)
        await locate(message)
    else:
        query = str(message.text).rstrip()
        msg, kb, msg2 = await look_for_price(query, message.from_user.id, len(users_retailers_tuple))
        if kb == 0:
            await bot.send_message(message.from_user.id, text=msg)
        else:
            await bot.send_message(message.from_user.id, text=msg, reply_markup=kb)
        if msg2 != "":
            await bot.send_message(message.from_user.id, text=msg2)


async def look_for_concrete_good_handler(callback: types.CallbackQuery):
    product_id = int(callback.data.split(" ")[2])
    msg, kb, msg2 = await look_for_concrete_good(product_id, callback.from_user.id)
    await bot.send_message(callback.from_user.id, msg, reply_markup=kb, parse_mode=types.ParseMode.HTML)
    if msg2 != "":
        await bot.send_message(callback.from_user.id, msg2)


async def prices_of_the_whole_list(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    list_id = int(callback.data.split()[2])
    list_content, exists = await product_list_content(list_id)
    if exists:
        for product in list_content:
            msg, kb, _ = await look_for_concrete_good(product_id=product[0], telegram_id=telegram_id)
            await bot.send_message(callback.from_user.id, text=msg, reply_markup=kb, parse_mode=types.ParseMode.HTML)

    else:
        msg = "Списка не существует. Выберите другой или создайте новый"
        await bot.send_message(callback.from_user.id, text=msg)


async def add_product_to_this_list(callback: types.CallbackQuery):
    list_id, product_id = int(callback.data.split()[1]), int(callback.data.split()[2])
    result = await add_product_to_user_list(list_id, product_id)
    await callback.answer(result, show_alert=True)


class FSMBug(StatesGroup):
    bug = State()


async def bug(message: types.Message):
    await FSMBug.bug.set()
    await bot.send_message(message.from_user.id, 'Опишите проблему, с которой столкнулись')


async def bug_report(message: types.Message, state: FSMContext):
    bug_text = message.text
    print(bug_text)
    if bug_text == "-":
        await state.finish()
        await bot.send_message(message.from_user.id, "Я готов работать дальше!")
    elif bug_text != "Мои списки" and bug_text != "Мои магазины" and bug_text != "Сообщить об ошибке":
        await state.finish()
        await create_bug_report(message.text)
        await bot.send_message(message.from_user.id, f'Спасибо, что помогаете развивать чат-бот, '
                                                     f'{message.from_user.first_name}!')
    else:
        await bot.send_message(message.from_user.id, 'Если вы передумали сообщать об ошибке, отправьте "-"')


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
    dp.register_message_handler(my_product_lists, Text(equals="Мои списки"))
    dp.register_callback_query_handler(insert_new_product_list, Text(equals="create new list"), state=None)
    dp.register_message_handler(add_new_list_by_name_handler, state=FSMForUserLists.name)
    dp.register_message_handler(bug, Text(equals='Сообщить об ошибке', ignore_case=True), state=None)
    dp.register_message_handler(bug_report, state=FSMBug.bug)
    dp.register_callback_query_handler(print_list_content, Text(startswith="lst"))
    dp.register_callback_query_handler(rename_product_list_handler, Text(startswith="rename list"))
    dp.register_message_handler(rename_product_list, state=FSMForRenameList.newName)
    dp.register_callback_query_handler(remove_product_from_list_handler, Text(startswith="rm g"))
    dp.register_callback_query_handler(remove_product_from_list, Text(startswith="rm prod"))
    dp.register_callback_query_handler(delete_list_by_name_handler, Text(startswith="rm l"))
    dp.register_callback_query_handler(look_for_concrete_good_handler, Text(startswith="lf g"))
    dp.register_callback_query_handler(prices_of_the_whole_list, Text(startswith="lf twl"))
    dp.register_callback_query_handler(add_product_to_this_list, Text(startswith="addptol"))
    dp.register_message_handler(look_for_price_handler)
