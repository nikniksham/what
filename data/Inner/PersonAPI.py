from data import db_session
from data.person import Person
from data.Inner.main_file import raise_error, check_person, check_password, check_admin


def find_by_id(id, session):
    person = session.query(Person).get(id)
    if not person:
        return raise_error(f"Аккаунт не найден", session)[0]
    return person, session


def get_self_person(email):
    person, session = check_person(email)
    if type(person) is dict:
        return person
    data = person.to_dict(only=('id', 'fullname', 'email', "orders"))
    session.close()
    return data


def put_self_person(email, args):
    person, session = check_person(email)
    if type(person) is dict:
        return person
    count = 0
    person_dict = person.to_dict(only=('fullname', 'email', 'orders'))
    keys = list(filter(lambda key: args[key] is not None and key in person_dict and args[key] != person_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'email':
            if session.query(Person).filter(Person.email == args["email"]).first():
                return raise_error("Этот email уже занят", session)[0]
            person.email = args['email']
        if key == 'fullname':
            person.fullname = args["fullname"]
        if key == 'orders':
            person.orders = args["orders"]
    if "change_password" in args:
        if not person.check_password(args["check_password"]):
            return raise_error("Пароль не совпадает с текущим паролем", session)[0]
        r, session = check_password(args['new_password'], session)
        if type(r) is dict:
            return r
        person.set_password(args['new_password'])
        count += 1
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    fullname = person.fullname
    session.close()
    return {"success": f"Пользователь {fullname} успешно изменён"}


def create_person(args):
    session = db_session.create_session()

    if not all(args[key] is not None for key in ['fullname', 'email', "new_password"]):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания аккаунта', session)[0]

    if session.query(Person).filter(Person.email == args['email']).first():
        return raise_error("Этот email уже занят", session)[0]

    res, session = check_password(args["new_password"], session)
    if type(res) is dict:
        return res

    new_person = Person()
    new_person.fullname = args["fullname"]
    new_person.email = args['email']
    new_person.balance = 0
    new_person.set_password(args["new_password"])
    new_person.type = "person"
    new_person.orders = ""

    session.add(new_person)
    session.commit()
    person_id = new_person.id
    session.close()

    return {'success': f'Админ {args["fullname"]} создан', 'id': int(person_id)}


def get_person_admin(admin_email, person_id):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    person = find_by_id(person_id, session)
    if type(person) is dict:
        return person
    data = person.to_dict(only=('id', 'fullname', 'email', 'orders'))
    session.close()
    return data


def person_order_change(email, order_id, is_add):
    person, session = check_person(email)
    if person is dict:
        return person

    order_id = str(order_id)
    orders = person.orders.split("|")

    if is_add and order_id not in orders:
        orders.append(order_id)
        person.orders = "|".join(orders)

    elif not is_add and order_id in orders:
        orders.remove(order_id)
        person.orders = orders

    session.commit()
    session.close()


def put_person_admin(admin_email, person_id, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin

    person = find_by_id(person_id, session)
    if type(person) is dict:
        return person

    count = 0
    person_dict = person.to_dict(only=('fullname', 'email', "balance", 'orders'))
    keys = list(filter(lambda key: args[key] is not None and key in person_dict and args[key] != person_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'email':
            if session.query(Person).filter(Person.email == args["email"]).first():
                return raise_error("Этот email уже занят", session)[0]
            person.email = args['email']
        if key == 'fullname':
            person.fullname = args["fullname"]
        if key == "balance":
            person.balance = args["balance"]
        if key == 'orders':
            person.orders = args['orders']
    if "change_password" in args:
        if not person.check_password(args["check_password"]):
            return raise_error("Пароль не совпадает с текущим паролем", session)[0]
        r, session = check_password(args['new_password'], session)
        if type(r) is dict:
            return r
        person.set_password(args['new_password'])
        count += 1
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    fullname = person.fullname
    session.close()
    return {"success": f"Пользователь {fullname} успешно изменён"}


def delete_person_admin(admin_email, admin_password, person_id):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]

    person = find_by_id(person_id, session)
    if type(person) is dict:
        return person
    fullname = person.fullname
    session.delete(person)
    session.commit()
    session.close()
    return {'success': f'Аккаунт {fullname} успешно удалён'}


def get_list_person_admin(admin_email):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    persons = session.query(Person).all()
    data = [item.to_dict(only=('id', 'fullname', 'email', 'orders')) for item in persons]
    session.close()
    return data
