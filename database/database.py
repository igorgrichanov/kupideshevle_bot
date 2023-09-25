import aiomysql
import asyncio
import config
import logging

logging.basicConfig(level=logging.INFO, filename="database_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


async def connect(query: str):
    result = 0
    try:
        conn = await aiomysql.connect(host=config.host_db_s,
                                      user=config.user_db_s, password=config.password_db_beget, db=config.name_db_s,
                                      loop=loop)
        async with conn.cursor() as cur:
            try:
                await cur.execute(query)
                if query[:6] == "SELECT":
                    result = await cur.fetchall()
            except Exception as exx:
                result = 1
                logging.error(exx, exc_info=True)
            await conn.commit()
        conn.close()
    except Exception as exc:
        logging.error(f"Connection failed: {exc}", exc_info=True)
    return result


async def product_list_content(list_id):
    query = (f'SELECT `product`.`id`, `product`.`name` FROM `product` '
             f'INNER JOIN `list_product` ON `list_product`.`product_id`=`product`.`id` '
             f'AND `list_product`.`list_id`={list_id};')
    result = await connect(query)
    query = f'SELECT * FROM `user_list` WHERE id={list_id}'
    list_existence = await connect(query)
    if len(list_existence) == 0:
        exists = False
    else:
        exists = True
    return result, exists


async def add_product_to_user_list(list_id: int, product_id: int):
    result = "Товар добавлен успешно!"
    query = f'INSERT INTO `list_product`(`list_id`, `product_id`) VALUES ({list_id}, {product_id});'
    status = await connect(query)
    if status == 1:
        result = "Товар уже есть в этом списке"
    return result


async def rename_product_list_query(old_name: str, new_name: str, telegram_id: int):
    result = "Изменения сохранены!"
    query = (f'UPDATE `user_list` SET name=\'{new_name}\' '
             f'WHERE `user_list`.`name`=\'{old_name}\' '
             f'AND `user_list`.`user_telegram_id`={telegram_id};')
    status = await connect(query)
    if status == 1:
        result = "Произошла ошибка! Пожалуйста, отправьте отзыв, нажав на кнопку на нижней клавиатуре, " \
                 "мы всё починим"
    return result


async def remove_product_from_list_query(list_id: int, product_id: int):
    result = "Товар уже был удалён прежде"
    query = (f'SELECT * FROM `list_product` '
             f'WHERE `list_product`.`list_id`={list_id} '
             f'AND `list_product`.`product_id`={product_id};')
    res = await connect(query)
    if len(res) != 0:
        query = (f'DELETE FROM `list_product` '
                 f'WHERE `list_product`.`list_id`={list_id} '
                 f'AND `list_product`.`product_id`={product_id};')
        await connect(query)
        result = "Изменения сохранены!"
    return result


async def add_new_product_list_query(telegram_id: int, list_name: str):
    result = ""
    query = f'SELECT `name` FROM `user_list` WHERE `name`=\'{list_name}\' AND `user_telegram_id`={telegram_id}'
    already_exists = await connect(query)
    if len(already_exists) == 0:
        query = f'INSERT INTO `user_list`(`name`, `user_telegram_id`) VALUES (\'{list_name}\', {telegram_id});'
        await connect(query)
    else:
        result = "Список с таким названием уже существует. Удалите его либо выберите другое название для " \
                 "нового списка"
    return result


async def delete_list_by_name_query(list_id: int):
    result = "Вы уже удалили этот список прежде"
    query = f'SELECT * FROM `user_list` WHERE id={list_id}'
    res = await connect(query)
    if len(res) != 0:
        query = f'DELETE FROM `user_list` WHERE id={list_id};'
        await connect(query)
        result = "Изменения сохранены"
    return result


async def user_product_lists(telegram_id: int):
    query = (f'SELECT `id`, `name` FROM `user_list` '
             f'WHERE `user_list`.`user_telegram_id`={telegram_id};')
    result = await connect(query)
    return result


async def select_all_available_retailers():
    query = f'SELECT `id`, `name` FROM `retailer` ORDER BY `id`;'
    result = await connect(query)
    return result


async def prices_of_known_product(product_id: int, telegram_id: int):
    query = (f'SELECT `product`.`name`, `retailer`.`name`, `retailer_has_product`.`price` FROM `product` '
             f'INNER JOIN `retailer_has_product` '
             f'ON `retailer_has_product`.`product_id`=`product`.`id`'
             f'INNER JOIN `fav_stores` '
             f'ON `fav_stores`.`retailer_id`=`retailer_has_product`.`retailer_id` '
             f'AND `fav_stores`.`user_telegram_id`={telegram_id} '
             f'INNER JOIN `retailer` '
             f'ON `fav_stores`.`retailer_id`=`retailer`.`id`'
             f'WHERE `product`.`id`={product_id};')
    result = await connect(query)
    return result


async def select_primitive_algorithm(product: str, telegram_id: int):
    query = (f'SELECT `product`.`id`, `product`.`name`, `retailer`.`name`, `retailer_has_product`.`price` '
             f'FROM `product`'
             f'INNER JOIN `retailer_has_product` '
             f'ON `retailer_has_product`.`product_id`=`product`.`id` AND '
             f'(`product`.`name` LIKE \'{product}%\' '
             f'OR `product`.`name` LIKE \'%{product}%\' '
             f'OR `product`.`name` LIKE \'%{product}\')'
             f'INNER JOIN `fav_stores` '
             f'ON `fav_stores`.`retailer_id`=`retailer_has_product`.`retailer_id` '
             f'AND `fav_stores`.`user_telegram_id`={telegram_id} '
             f'INNER JOIN `retailer` '
             f'ON `fav_stores`.`retailer_id`=`retailer`.`id`;')
    result = await connect(query)
    if len(result) == 0 and product.find(" ") > 0:
        truncated_query = product[:product.rfind(" ")]
        result = await select_primitive_algorithm(truncated_query, telegram_id)
    return result


async def delete_retailer_added_by_user(telegram_id, retailer_id):
    query = (f'SELECT `retailer_id` FROM `fav_stores` WHERE '
             f'`user_telegram_id`={telegram_id} AND `retailer_id`={retailer_id};')
    res = await connect(query)
    if len(res) == 0:
        return False
    query = (f'DELETE FROM `fav_stores` WHERE `user_telegram_id`={telegram_id} '
             f'AND `retailer_id`={retailer_id};')
    await connect(query)
    return True


async def select_retailers_added_by_user(telegram_id):
    query = (f'SELECT id, name FROM `retailer` '
             f'INNER JOIN `fav_stores` '
             f'ON `retailer`.`id` = `fav_stores`.`retailer_id` '
             f'AND `fav_stores`.`user_telegram_id` = {telegram_id} '
             f'ORDER BY `retailer`.`id`;')
    result = await connect(query)
    return result


async def add_retailer_to_user_list(telegram_id, retailer_id):
    result = "Магазин добавлен успешно!"
    query = (f'INSERT INTO `fav_stores` (`user_telegram_id`, `retailer_id`) VALUES '
             f'(\'{telegram_id}\', \'{retailer_id}\');')
    status = await connect(query)
    if status == 1:
        result = "Вы уже добавили этот магазин"
    return result


async def create_bug_report(report: str):
    query = f'INSERT INTO `bug_report` (`text`) VALUES (\'{report}\');'
    await connect(query)


async def insert_new_user(user_id: int):
    query = f'INSERT INTO `user` VALUES ({user_id});'
    result = await connect(query)
    return result


async def is_user_registered(user_id: int):
    query = f'SELECT * FROM `user` WHERE id={user_id}'
    result = await connect(query)
    return result


loop = asyncio.get_event_loop()
# loop.run_until_complete(look_for_prices_in_selected_retailers(20, 582576913))
