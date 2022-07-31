from data import db_session
from data.Inner.main_file import raise_error, check_person, check_admin
from data.product import Product
from data.ticket import Ticket


def find_by_id(id, session):
    ticket = session.query(Ticket).get(id)
    if not ticket:
        return raise_error(f"Тикет не найден", session)[0]
    return ticket, session


def get_ticket_by_id(ticket_id):
    session = db_session.create_session()
    ticket, session = find_by_id(ticket_id, session)
    if type(ticket) is dict:
        return ticket
    data = ticket.to_dict()
    session.close()
    return data


def get_list_tickets_person(email):
    person, session = check_person(email)
    if person is dict:
        return person
    tickets = session.query(Ticket).filter(Ticket.person_id == person.id).all()
    data = [item.to_dict(only=("id", "price")) for item in tickets]
    session.close()
    return data


def get_list_tickets_admin(email):
    admin, session = check_admin(email)
    if admin is dict:
        return admin
    tickets = session.query(Ticket).all()
    data = [item.to_dict(only=("id", "price")) for item in tickets]
    session.close()
    return data


def delete_ticket(email, ticket_id):
    person, session = check_admin(email)
    if person is dict:
        return person
    ticket, session = find_by_id(ticket_id, session)
    if type(ticket) is dict:
        return ticket
    if ticket.person_id != person.id:
        return raise_error("Для этого у вас недостаточно прав", session)[0]
    person.balance += ticket.price
    session.delete(ticket)
    session.commit()
    session.close()
    return {'success': f'Заявка удалена'}


def create_ticket(email, args):
    person, session = check_person(email)
    if type(person) is dict:
        return person
    if not all(args[key] is not None for key in ["product_id"]):
        return raise_error('Пропущены некоторые аргументы, необходимые для тикета', session)[0]
    product = session.query(Product).get(args["product_id"])
    if not product:
        return raise_error("Товар не найден", session)[0]
    if person.balance < product.good_price:
        return raise_error("У вас недостаточно средств для этого", session)[0]
    new_ticket = Ticket()
    new_ticket.price = product.good_price
    new_ticket.is_block = False
    person.balance -= product.good_price
    product.add(new_ticket)
    person.add(new_ticket)
    session.merge(person)
    session.merge(product)
    session.commit()
    ticket_id = new_ticket.id
    session.close()
    return {'success': f'Тикет {args["name"]} создан', 'id': int(ticket_id)}
