from sqlalchemy import and_
from data import db_session
from data.Inner.main_file import raise_error, check_admin
from data.order import Order
from data.person import Person
from data.product import Product


def find_by_id_product(id, session):
    return session.query(Product).get(id), session


def find_by_id(id, session):
    order = session.query(Order).get(id)
    if not order:
        return raise_error(f"Заказ не найден", session)
    return order, session


def get_order_by_id(order_id):
    session = db_session.create_session()
    order, session = find_by_id(order_id, session)
    if type(order) is dict:
        return order
    data = order.to_dict()
    session.close()
    return data


def get_list_orders(email):
    admin, session = check_admin(email)
    orders = session.query(Order).all()
    data = [item.to_dict(only=("id", "prod_id", "current", "max", "status", 'info')) for item in orders]
    session.close()
    return data


def get_list_orders_by_indexes(user_id, indexes):
    session = db_session.create_session()
    data = []
    for index in indexes:
        order = session.query(Order).get(index)
        if order:
            product, session = find_by_id_product(order.prod_id, session)
            if product:
                users = {}
                for el in order.info.split("|"):
                    if el == "":
                        continue
                    us, c = el.split(":")
                    users[int(us)] = int(c)
                di = order.to_dict(only=("id", "prod_id", "current", "max", "status", 'info'))
                di["user_count"] = users[user_id]
                di["user_price"] = users[user_id] * product.good_price
                di["product"] = product.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count",
                                                      'good_price', "in_stoke", "image", "id", "description", "specifications"))
                data.append(di)
    session.close()
    return data


def get_list_orders_by_product(prod_id):
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.prod_id == prod_id).all()
    data = [item.to_dict(only=("id", "prod_id", "current", "max", "status", 'info')) for item in orders]
    session.close()
    return data


def get_order_by_product(prod_id):
    session = db_session.create_session()
    data, session = order_ficha(prod_id, session)
    session.close()
    return data


def get_orders_by_product_indexes(prod_indexes):
    session = db_session.create_session()
    orders = {}
    for index in prod_indexes:
        orders[index], session = order_ficha(index, session, True)
    session.close()
    return orders


def order_ficha(prod_id, session, f=False, product=None):
    if not product:
        product, session = find_by_id_product(prod_id, session)
    if not product:
        if f:
            return None, session
        return raise_error("Не нашлося", session)
    orders = session.query(Order).filter(and_(Order.prod_id == prod_id, Order.status == 0)).all()
    if orders:
        data = [item.to_dict(only=("id", "prod_id", "current", "max", "status", 'info')) for item in orders][0]
    else:
        order, session = create_order_func({"info": '', "prod_id": prod_id, "max": product.good_count, "current": 0}, session)
        data = order.to_dict(only=("id", "prod_id", "current", "max", "status", 'info'))
    return data, session


def put_order(order_id, args):
    session = db_session.create_session()
    order, session = find_by_id(order_id, session)
    if type(order) is dict:
        return order
    count = 0
    order_dict = order.to_dict(only=("info", "current", "max", "status", "prod_id"))
    keys = list(filter(lambda key: args[key] is not None and key in order_dict and args[key] != order_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'info':
            order.info = args["info"]
        if key == "status":
            order.status = args["status"]
        if key == "prod_id":
            order.prod_id = args["prod_id"]
        if key == "current":
            order.current = args["current"]
        if key == "max":
            order.max = args["max"]
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    session.close()
    return {"success": f"Заказ {order_id} успешно изменён"}


def create_orders_by_info(info, user_id):
    session = db_session.create_session()
    user = session.query(Person).get(user_id)
    for key, val in info.items():
        product, session = find_by_id_product(key, session)
        if product:
            while val[0]:
                orders = session.query(Order).filter(and_(Order.prod_id == key, Order.status == 0)).all()
                if orders:
                    order = orders[0]
                else:
                    order, session = create_order_func({"info": '', "prod_id": key, "max": product.good_count, "current": 0}, session)
                session, res = change_info(session, order, user_id, val, user)
                if "remains" in res:
                    val[0] = res["remains"]
                else:
                    val[0] = 0
    session.commit()
    session.close()
    return {"success": "Всё успешно изменено"}


def change_info(session, order, user_id, info, user):
    if order.status != 0:
        return raise_error("заказ уже в обработке, его нельзя менять")[0]
    users, cur = {}, 0
    # print(order.info)
    for el in order.info.split("|"):
        if el == "":
            continue
        us, c = el.split(":")
        users[int(us)] = int(c)
        cur += int(c)
    if user_id not in users:
        users[user_id] = 0
    add_f = True
    # print(info)
    # print(users)
    if info[0] < 0:
        if users[user_id] - info[0] <= 0:
            del users[user_id]
            res, add_f = {"success": "пользователь удалён из заказа", "id": 0}, False
        else:
            users[user_id] -= info[0]
            res = {"success": "пользователь уменьшил кол-во заказа", "id": 1}
    else:
        if order.current + info[0] >= order.max:
            order.status = 1
            lch = order.max - order.current
            users[user_id] += lch
            res = {"success": "заказ пошёл в обработку", "id": 2, "remains": min(info[0] - lch, order.max * 5)}
        else:
            users[user_id] += info[0]
            res = {"success": "пользователь увеличил кол-во заказа", 'id': 3}
    # print(users)
    user_orders = {}
    for el in user.orders.split("|"):
        if el == "":
            continue
        ord, c = el.split(":")
        user_orders[int(ord)] = int(c)
    if add_f:
        user_orders[order.id] = users[user_id]
    elif user_id in user_orders:
        del user_orders[order.id]

    user.orders = "|".join([f"{key}:{user_orders[key]}" for key in user_orders.keys()])

    order.current = sum([users[key] for key in users.keys()])
    order.info = "|".join([f"{key}:{users[key]}" for key in users.keys()])
    session.commit()
    return session, res


def delete_order(admin_email, admin_password, order_id):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")
    order, session = find_by_id(order_id, session)
    if type(order) is dict:
        return order
    session.delete(order)
    session.commit()
    session.close()
    return {'success': f'Заказ успешно удалён'}


def create_order(args):
    session = db_session.create_session()
    if not all(args[key] is not None for key in ["info", "max", "current", "prod_id"]):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания товара', session)[0]

    new_order, session = create_order_func(args, session)

    order_id = new_order.id

    session.close()
    return {'success': f'Заказ {order_id} создан', 'id': int(order_id)}


def create_order_func(args, session):
    new_order = Order()
    new_order.status = 0
    new_order.info = args['info']
    new_order.prod_id = args['prod_id']
    new_order.current = args['current']
    new_order.max = args['max']
    session.add(new_order)
    session.commit()
    return new_order, session
