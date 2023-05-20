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


async def look_for_prices_in_added_retailers(telegram_id, product_id):
    added_retailers = await select_retailers_id_added_by_user(telegram_id)
    result = []
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            for retailer_id in added_retailers:
                try:
                    await cur.execute(f'SELECT `price` FROM `mydb`.`retailer_has_product` WHERE '
                                      f'`product_id`={product_id} AND `retailer_id`={retailer_id};')
                    retailer_tuple = await cur.fetchall()
                    product_price = retailer_tuple[0][0]
                    retailer_name = await get_retailer_name(retailer_id)
                    result.append([retailer_name, product_price])
                except Exception as ex:
                    print(ex)
                await conn.commit()
        conn.close()
        return result
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def select_retailers_id_added_by_user(telegram_id):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'SELECT `retailer_id` FROM `mydb`.`fav_stores` WHERE '
                                  f'`user_telegram_id`={telegram_id};')
                retailer_tuple = await cur.fetchall()
                result = []
                if len(retailer_tuple) > 0:
                    for retailer_id_tuple in retailer_tuple:
                        result.append(retailer_id_tuple[0])
            except Exception as ex:
                print(ex)
            await conn.commit()
        conn.close()
        return result
    except Exception as ex:
        print("Connection failed")
        print(ex)


async def select_primitive_algorithm(query: str):
    res = tuple()
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'SELECT * FROM `mydb`.`product` WHERE `name`=\'{query}\';')
                res = await cur.fetchall()
                if len(res) == 0 and query.find(" ") > 0:
                    truncated_query = query[:query.rfind(" ")]
                    res = await select_primitive_algorithm(truncated_query)
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


async def select_retailers_name_added_by_user(telegram_id):
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


async def get_retailer_name(retailer_id):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='root', db='mydb',
                                      loop=loop)
        print("Connected successfully")
        async with conn.cursor() as cur:
            try:
                await cur.execute(f'SELECT `name` FROM `mydb`.`retailer` WHERE `id`={retailer_id}')
                retailer = await cur.fetchall()
            except Exception as ex:
                print("entry already exists:", ex)
            await conn.commit()
        conn.close()
        return retailer[0][0]
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
