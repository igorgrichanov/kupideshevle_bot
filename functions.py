from database import select_all_available_retailers, select_retailers_name_added_by_user
from keyboards import create_retailers_kb, create_inline_button


async def available_retailers_keyboard():
    retailers = await select_all_available_retailers()
    kb = await create_retailers_kb(3)
    for retailer in retailers:
        button = await create_inline_button(text=retailer[1], callback=f'add retailer {retailer[0]}')
        kb.insert(button)
    ready_button = await create_inline_button(text="Готово", callback="add retailer -1")
    kb.add(ready_button)
    return kb


async def users_retailers_keyboard(telegram_id):
    retailers = await select_retailers_name_added_by_user(telegram_id)
    kb = await create_retailers_kb(len(retailers))
    for retailer in retailers:
        button = await create_inline_button(text=retailer[1], callback=f'remove retailer {retailer[0]}')
        kb.insert(button)
    ready_button = await create_inline_button(text="Готово", callback="remove retailer -1")
    kb.add(ready_button)
    return kb
