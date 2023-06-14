from aiogram import types, Dispatcher
from create_bot import bot
from aiogram.dispatcher.filters import Text
from keyboards import kb_markup_main, location_markup, my_retailers_delete_add
from database import insert_new_user, create_bug_report, add_retailer_to_user_list, \
    select_retailers_added_by_user, delete_retailer_added_by_user, select_primitive_algorithm, user_product_list, \
    add_new_product_list_query, add_product_to_user_list, prices_of_known_product
from functions import available_retailers_keyboard, users_retailers_keyboard, found_goods_keyboard, list_actions, \
    available_lists, add_product_to_list, lists_to_add_products
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


async def my_product_lists(message: types.Message):
    lists = await user_product_list(message.from_user.id)
    if len(lists) == 0:
        kb = await list_actions(True)
        await bot.send_message(message.from_user.id, "У вас пока нет ни одного списка",
                               reply_markup=kb)
    else:
        msg = ""
        i = 1
        for lst in lists:
            msg += f'{i}. {lst[1]}\n'
            i += 1
        msg.rstrip(" ")
        kb = await list_actions(False)
        await bot.send_message(message.from_user.id, msg, reply_markup=kb)


async def explore_list(callback: types.CallbackQuery):
    kb = await available_lists(callback.from_user.id)
    await bot.send_message(callback.from_user.id, text="Какой список хотите просмотреть?", reply_markup=kb)


#async def print_list_content(callback: types.CallbackQuery):


class FSMForUserLists(StatesGroup):
    name = State()


async def insert_new_product_list(telegram_id: int):
    await FSMForUserLists.name.set()
    await sleep(1)
    await bot.send_message(telegram_id, "Отправьте имя нового списка")


async def add_new_list_by_name_handler(message: types.Message, state: FSMContext):
    list_name = message.text
    if list_name == "-":
        await state.finish()
        await bot.send_message(message.from_user.id, "Я готов работать дальше!")
    elif list_name != "Мои списки" and list_name != "Мои магазины" and list_name != "Сообщить об ошибке":
        result = await add_new_product_list_query(message.from_user.id, message.text)
        await state.finish()
        if result != "":
            await bot.send_message(message.from_user.id, result)
        else:
            await bot.send_message(message.from_user.id, "Список успешно создан!\n\nВы можете пролистать выше и "
                                                         "добавить товары в созданный список")
    else:
        await bot.send_message(message.from_user.id, 'Если вы передумали создавать список, отправьте знак "-"')


async def delete_list_by_name_handler(message: types.Message):
    pass
    #написать


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
        await locate(message)
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
                    msg += f'{info[2]} - {info[3]} руб.\n'
                msg.rstrip(" ")
                kb = await add_product_to_list(tuple_from_database[0][0])
                if not await are_there_any_lists(message.from_user.id):
                    await bot.send_message(message.from_user.id,
                                           "Вы можете создать список, чтобы затем искать цены сразу "
                                           "на несколько товаров. Попробуйте!")
                await bot.send_message(message.from_user.id, text=msg, reply_markup=kb)
            else:
                await bot.send_message(message.from_user.id, text="Были найдены цены на следующие товары. Если в этом "
                                                                  "списке есть тот, который вас интересует - отправьте "
                                                                  "его в чат, чтобы узнать цены")
                await sleep(2)

                kb, msg = await found_goods_keyboard(tuple_from_database)
                await bot.send_message(message.from_user.id, text=msg, reply_markup=kb)


async def look_for_concrete_good(callback: types.CallbackQuery):
    product_id = int(callback.data.split(" ")[1])
    tuple_from_database = await prices_of_known_product(product_id, callback.from_user.id)
    msg = ""
    for info in tuple_from_database:
        msg += f'{info[1]} - {info[2]} руб.\n'
    msg.rstrip(" ")
    kb = await add_product_to_list(product_id)

    await bot.send_message(callback.from_user.id, text=msg, reply_markup=kb)
    if not await are_there_any_lists(callback.from_user.id):
        await bot.send_message(callback.from_user.id, "Вы можете создать список, чтобы затем искать цены сразу "
                                                     "на несколько товаров. Попробуйте!")


async def are_there_any_lists(telegram_id: int):
    lists = await user_product_list(telegram_id)
    if len(lists) == 0:
        return False
    else:
        return True


class FSMForProductAdding(StatesGroup):
    choosingList = State()


async def add_product_to_list_by_name(callback: types.CallbackQuery):
    await FSMForProductAdding.choosingList.set()
    product_id = int(callback.data.split(" ")[1])
    user_lists = await user_product_list(callback.from_user.id)
    if len(user_lists) != 0:
        kb = await lists_to_add_products(callback.from_user.id, product_id)
        await bot.send_message(callback.from_user.id, text="В какой список добавим продукт?", reply_markup=kb)
    else:
        await bot.send_message(callback.from_user.id, text="У вас пока нет ни одного списка. Самое время создать "
                                                           "первый!")
        await insert_new_product_list(callback.from_user.id)


async def add_product_to_this_list(callback: types.CallbackQuery, state: FSMContext):
    list_id, product_id = int(callback.data.split()[1]), int(callback.data.split()[2])
    result = await add_product_to_user_list(list_id, product_id)
    await callback.answer(result, show_alert=True)
    await state.finish()
    # а если хочет добавить в несколько списков?


async def dont_want_anymore_to_add_product_to_list(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, text="Если вы передумали добавлять товар в список, продублируйте "
                                                      "только что отправленное сообщение")
    await state.finish()


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
        await bot.send_message(message.from_user.id, 'Спасибо, что помогаете '
                                                     'развивать чат-бот!')
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
    dp.register_callback_query_handler(explore_list, Text(equals="explore lists"))
    dp.register_message_handler(bug_report, state=FSMBug.bug)
    dp.register_callback_query_handler(look_for_concrete_good, Text(startswith="lf"))
    dp.register_callback_query_handler(add_product_to_list_by_name, Text(startswith="addp"))
    dp.register_callback_query_handler(add_product_to_this_list, Text(startswith="addptol"),
                                       state=FSMForProductAdding.choosingList)
    dp.register_message_handler(dont_want_anymore_to_add_product_to_list, state=FSMForProductAdding.choosingList)
    dp.register_message_handler(look_for_price)
