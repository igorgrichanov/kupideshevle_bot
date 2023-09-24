from database import select_all_available_retailers, select_retailers_added_by_user, user_product_lists, \
    product_list_content
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
    msg = "Были найдены цены на следующие товары. Если в этом списке есть тот, который вас интересует - нажмите на " \
          "кнопку с его номером\n\n"
    i = 1
    kb = await create_inline_kb(5)
    for info in tuple_from_database:
        distinct_res[info[0]] = distinct_res.get(info[0], 0) + 1
        if distinct_res[info[0]] == 1:
            msg += f'{i}. {info[1]}\n'
            button = await create_inline_button(text=f'{i}', callback=f'lf g {info[0]}')
            kb.insert(button)
            i += 1
    msg.rstrip(" ")
    return kb, msg


async def user_product_lists_keyboard(telegram_id: int):
    flag = False
    lists = await user_product_lists(telegram_id)
    kb = await create_inline_kb(2)
    create_new_list_button = await create_inline_button(text="Создать новый список", callback="create new list")
    kb.add(create_new_list_button)
    if len(lists) > 0:
        for lst in lists:
            button = await create_inline_button(text=lst[1], callback=f'lst {lst[0]} {lst[1]}')
            if not flag:
                kb.add(button)
                flag = True
            else:
                kb.insert(button)
    return kb, flag


async def concrete_list_actions(empty: bool, list_id: int, list_name: str):
    kb = await create_inline_kb(2)
    remove_list_button = await create_inline_button(text="Удалить список",
                                                    callback=f"rm l {list_id}")
    rename_list_button = await create_inline_button(text="Переименовать список",
                                                    callback=f"rename list {list_name}")
    remove_good_button = await create_inline_button(text=f"Удалить товар", callback=f"rm g from {list_id}")
    look_for_the_whole_list_button = await create_inline_button(text="Найти цены на все товары",
                                                                callback=f"lf twl {list_id}")
    kb.add(rename_list_button)
    kb.add(remove_list_button)
    if not empty:
        kb.insert(remove_good_button)
        kb.insert(look_for_the_whole_list_button)
    return kb


async def add_product_to_list(telegram_id: int, product_id: int):
    kb = await create_inline_kb(3)
    lists = await user_product_lists(telegram_id)
    if len(lists) > 0:
        for lst in lists:
            button = await create_inline_button(text=f'В {lst[1]}', callback=f'addptol {lst[0]} {product_id}')
            kb.insert(button)
    else:
        button = await create_inline_button(text="Создать новый список", callback="create new list")
        kb.insert(button)
    return kb


async def remove_product_from_list_keyboard(list_id: int):
    kb = await create_inline_kb(5)
    products = await product_list_content(list_id)
    i = 1
    for prod in products[0]:
        button = await create_inline_button(text=f'{i}', callback=f'rm prod {prod[0]} {list_id}')
        kb.insert(button)
        i += 1
    return kb
