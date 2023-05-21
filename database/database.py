import aiomysql
import asyncio


async def select_all_available_retailers():
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'SELECT `id`, `name` FROM `mydb`.`retailer` ORDER BY `id`;')
                result = await cur.fetchall()
            except Exception as ex:
                print(ex)
            await conn.commit()
        conn.close()
        return result
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def select_primitive_algorithm(query: str, telegram_id: int):
    res = tuple()
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'SELECT `mydb`.`product`.`name`, `mydb`.`retailer`.`name`, '
                                  f'`mydb`.`retailer_has_product`.`price` '
                                  f'FROM `mydb`.`product`'
                                  f'INNER JOIN `mydb`.`retailer_has_product` '
                                  f'ON `mydb`.`retailer_has_product`.`product_id`=`mydb`.`product`.`id` AND '
                                  f'(`mydb`.`product`.`name` LIKE \'{query}%\' '
                                  f'OR `mydb`.`product`.`name` LIKE \'%{query}\') '
                                  f'INNER JOIN `mydb`.`fav_stores` '
                                  f'ON `mydb`.`fav_stores`.`retailer_id`=`mydb`.`retailer_has_product`.`retailer_id` '
                                  f'AND `mydb`.`fav_stores`.`user_telegram_id`={telegram_id} '
                                  f'INNER JOIN `mydb`.`retailer` '
                                  f'ON `mydb`.`fav_stores`.`retailer_id`=`mydb`.`retailer`.`id`;')
                res = await cur.fetchall()
                if len(res) == 0 and query.find(" ") > 0:
                    truncated_query = query[:query.rfind(" ")]
                    res = await select_primitive_algorithm(truncated_query, telegram_id)
            except Exception as ex:
                print(ex)
            await conn.commit()
        conn.close()
        return res
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def delete_retailer_added_by_user(telegram_id, retailer_id):
    result = True
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'SELECT `retailer_id` FROM `mydb`.`fav_stores` WHERE '
                                  f'`user_telegram_id`={telegram_id} AND `retailer_id`={retailer_id};')
                res = await cur.fetchall()
                if len(res) == 0:
                    result = False
            except Exception as ex:
                print(ex)
            try:
                await cur.execute(f'DELETE FROM `mydb`.`fav_stores` WHERE `user_telegram_id`={telegram_id} '
                                  f'AND `retailer_id`={retailer_id};')
            except Exception as ex:
                print("entry does not exist:", ex)
            await conn.commit()
        conn.close()
        return result
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def select_retailers_added_by_user(telegram_id):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'SELECT id, name FROM `mydb`.`retailer` '
                                  f'INNER JOIN `mydb`.`fav_stores` '
                                  f'ON `mydb`.`retailer`.`id` = `mydb`.`fav_stores`.`retailer_id` '
                                  f'AND `mydb`.`fav_stores`.`user_telegram_id` = {telegram_id} '
                                  f'ORDER BY `mydb`.`retailer`.`id`;')
                result = await cur.fetchall()
            except Exception as ex:
                print(ex)
            await conn.commit()
        conn.close()
        return result
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def add_retailer_to_user_list(telegram_id, retailer_id):
    result = "Магазин добавлен успешно!"
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'INSERT INTO `mydb`.`fav_stores` (`user_telegram_id`, `retailer_id`) VALUES '
                                  f'(\'{telegram_id}\', \'{retailer_id}\');')
            except Exception as ex:
                print("entry already exists:", ex)
                result = "Вы уже добавили этот магазин"
            await conn.commit()
        conn.close()
        return result
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def create_bug_report(report):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'INSERT INTO `mydb`.`bug_report` (`text`) VALUES (\'{report}\');')
            except Exception as ex:
                print(ex)
            await conn.commit()
        conn.close()
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def insert_new_user(user_id):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'INSERT INTO mydb.user VALUES ({user_id});')
            except Exception as ex:
                print("Entry already exists", ex)
            await conn.commit()
        conn.close()
    except Exception as ex:
        print("Connection failed")
        print(ex)


loop = asyncio.get_event_loop()
# loop.run_until_complete(look_for_prices_in_selected_retailers(20, 582576913))
