from sqlalchemy import and_
from data import db_session
from data.Inner.main_file import raise_error, check_admin
from data.order import Order


def find_by_id(id, session):
    order = session.query(Order).get(id)
    if not order:
        return raise_error(f"Заказ не найден", session)[0]
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


def get_list_orders_by_product(prod_id):
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.prod_id == prod_id).all()
    data = [item.to_dict(only=("id", "prod_id", "current", "max", "status", 'info')) for item in orders]
    session.close()
    return data


def get_order_by_product(prod_id):
    session = db_session.create_session()
    orders = session.query(Order).filter(and_(Order.prod_id == prod_id, Order.status == 0)).all()
    data = [item.to_dict(only=("id", "prod_id", "current", "max", "status", 'info')) for item in orders]
    session.close()
    return data


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


def change_info(order_id, user_id, change):
    session = db_session.create_session()
    order, session = find_by_id(order_id, session)
    if type(order) is dict:
        return order
    if order.status != 0:
        return raise_error("заказ уже в обработке, его нельзя менять", session)[0]
    users, cur = {}, 0
    for el in order.info.split("|"):
        if el == "":
            continue
        us, c = el.split(":")
        users[int(us)] = int(c)
        cur += int(c)
    if user_id not in users:
        users[user_id] = 0
    if change < 0:
        if users[user_id] - change <= 0:
            del users[user_id]
            res = {"success": "пользователь удалён из заказа", "id": 0}
        else:
            users[user_id] -= change
            res = {"success": "пользователь уменьшил кол-во заказа", "id": 1}
    else:
        if order.current + change >= order.max:
            order.status = 1
            lch = order.max - order.current
            users[user_id] += lch
            res = {"success": "заказ пошёл в обработку", "id": 2, "remains": min(change - lch, order.max)}
        else:
            users[user_id] += change
            res = {"success": "пользователь увеличил кол-во заказа", 'id': 3}
    order.current = sum([users[key] for key in users.keys()])
    order.info = "".join([f"{key}:{users[key]}" for key in users.keys()])
    session.commit()
    return res


def delete_order(admin_email, admin_password, order_id):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]
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

    new_order = Order()
    new_order.status = 0
    new_order.info = args['info']
    new_order.prod_id = args['prod_id']
    new_order.current = args['current']
    new_order.max = args['max']
    session.add(new_order)
    session.commit()
    order_id = new_order.id
    session.close()
    return {'success': f'Заказ {order_id} создан', 'id': int(order_id)}
