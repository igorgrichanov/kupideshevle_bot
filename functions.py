from database import select_all_available_retailers, select_retailers_added_by_user, user_product_list
from keyboards import create_inline_kb, create_inline_button


async def available_retailers_keyboard():
    retailers = await select_all_available_retailers()
    kb = await create_inline_kb(3)
    for retailer in retailers:
        button = await create_inline_button(text=retailer[1], callback=f'add retailer {retailer[0]}')
        kb.insert(button)
    ready_button = await create_inline_button(text="Готово", callback="add retailer -1")
    kb.add(ready_button)
    return kb


async def users_retailers_keyboard(telegram_id):
    retailers = await select_retailers_added_by_user(telegram_id)
    kb = await create_inline_kb(3)
    for retailer in retailers:
        button = await create_inline_button(text=retailer[1], callback=f'remove retailer {retailer[0]}')
        kb.insert(button)
    ready_button = await create_inline_button(text="Готово", callback="remove retailer -1")
    kb.add(ready_button)
    return kb


async def found_goods_keyboard(tuple_from_database: tuple):
    distinct_res = dict()
    msg = ""
    i = 1
    kb = await create_inline_kb(5)
    for info in tuple_from_database:
        distinct_res[info[0]] = distinct_res.get(info[0], 0) + 1
        if distinct_res[info[0]] == 1:
            msg += f'{i}. {info[1]}\n'
            button = await create_inline_button(text=f'{i}', callback=f'lf {info[0]}')
            kb.insert(button)
            i += 1
    msg.rstrip(" ")
    return kb, msg


async def list_actions(empty: bool):
    kb = await create_inline_kb(2)
    add_new_product_list_button = await create_inline_button(text="Создать список", callback="create new list")
    rm_product_list_button = await create_inline_button(text="Удалить список", callback="remove list")
    explore_lists_button = await create_inline_button(text="Просмотреть содержимое", callback="explore lists")
    kb.add(add_new_product_list_button)
    if not empty:
        kb.insert(rm_product_list_button)
        kb.add(explore_lists_button)
    return kb


async def available_lists(telegram_id: int):
    kb = await create_inline_kb(5)
    lists = await user_product_list(telegram_id)
    for lst in lists:
        button = await create_inline_button(text=lst[1], callback=f'l {lst[0]}')
        kb.insert(button)
    return kb


async def add_product_to_list(product_id: int):
    kb = await create_inline_kb(1)
    button = await create_inline_button(text="Добавить в список", callback=f"addp {product_id}")
    kb.insert(button)
    return kb


async def lists_to_add_products(telegram_id: int, product_id: int):
    kb = await create_inline_kb(3)
    lists = await user_product_list(telegram_id)
    for lst in lists:
        button = await create_inline_button(text=lst[1], callback=f'addptol {lst[0]} {product_id}')
        kb.insert(button)
    return kb
#сразу на кнопке писать названия списков
