from data import db_session
from data.Inner.main_file import raise_error, check_admin
from data.order import Order
from data.ticket import Ticket


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
    data = [item.to_dict(only=("it", "tik_id")) for item in orders]
    session.close()
    return data


def put_order(admin_email, order_id, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    order, session = find_by_id(order_id, session)
    if type(order) is dict:
        return order
    count = 0
    order_dict = order.to_dict(only=("tik_id"))
    keys = list(filter(lambda key: args[key] is not None and key in order_dict and args[key] != order_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'tik_id':
            order.tik_id = args["tik_id"]
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    session.close()
    return {"success": f"Заказ {id} успешно изменён"}


def delete_order(admin_email, admin_password, order_id):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]
    order, session = find_by_id(order_id, session)
    if type(order) is dict:
        return order
    tickets = session.query(Order).filter(Ticket.id in list(map(int, order.tik_id.split("/")))).all()
    if tickets:
        for ticket in tickets:
            session.delete(ticket)
    session.delete(order)
    session.commit()
    session.close()
    return {'success': f'Заказ со всеми тикетами успешно удалён'}


def create_order(args):
    session = db_session.create_session()
    if not all(args[key] is not None for key in ["tik_id"]):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания товара', session)[0]
    for tid in list(map(int, args["tik_id"].split("/"))):
        ticket = session.query(Ticket).get(tid)
        if ticket and not ticket.is_block:
            ticket.is_block = True
        else:
            return raise_error("Беды с тикетами", session)[0]
    new_order = Order()
    new_order.tik_id = args["tik_id"]
    session.add(new_order)
    session.commit()
    order_id = new_order.id
    session.close()
    return {'success': f'Заказ {order_id} создан', 'id': int(order_id)}
