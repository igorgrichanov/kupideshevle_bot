from src.database import user_product_lists, select_primitive_algorithm, prices_of_known_product
from src.keyboards import add_product_to_list, found_goods_keyboard


async def are_there_any_lists(telegram_id: int):
    lists = await user_product_lists(telegram_id)
    if len(lists) == 0:
        return False
    else:
        return True


async def look_for_price(query: str, telegram_id: int, retailers_total: int):
    tuple_from_database = await select_primitive_algorithm(query, telegram_id)
    if len(tuple_from_database) == 0:
        msg = "Я пока не знаю цены на данную категорию.\n\nПопробуйте уточнить запрос в соответствии с требуемым " \
              "форматом или найти другой товар"
        return msg, 0, ""
    else:
        if len(tuple_from_database) <= retailers_total:
            msg = ""
            for info in tuple_from_database:
                msg += f'{info[2]} - {info[3]} руб.\n'
            msg += "\nДобавим товар в список?"
            kb = await add_product_to_list(telegram_id, tuple_from_database[0][0])
            if not await are_there_any_lists(telegram_id):
                msg2 = "Вы можете создать список, чтобы затем искать цены сразу на несколько товаров. Попробуйте!"
                return msg, kb, msg2
            else:
                return msg, kb, ""
        else:
            kb, msg = await found_goods_keyboard(tuple_from_database)
            return msg, kb, ""


async def look_for_concrete_good(product_id: int, telegram_id: int):
    tuple_from_database = await prices_of_known_product(product_id, telegram_id)
    msg = f"<b>{tuple_from_database[0][0]}</b>\n\n"
    for info in tuple_from_database:
        msg += f'{info[1]} - {info[2]} руб.\n'
    msg += "\nДобавим товар в список?"
    kb = await add_product_to_list(telegram_id, product_id)
    if not await are_there_any_lists(telegram_id):
        msg2 = "Вы можете создать список, чтобы затем искать цены сразу на несколько товаров. Попробуйте!"
        return msg, kb, msg2
    else:
        return msg, kb, ""
