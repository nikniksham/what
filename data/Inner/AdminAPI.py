from data.admin import Admin
from data.person import Person
from data.Inner.main_file import raise_error, check_admin, check_password


def find_by_id(id, session):
    admin = session.query(Admin).get(id)
    if not admin:
        return raise_error(f"Админ не найден", session)[0]
    return admin, session


def get_self_admin(admin_email):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    data = admin.to_dict(only=('id', 'fullname', 'email', "type"))
    session.close()
    return data


def get_list_admin(admin_email):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    admins = session.query(Admin).all()
    data = [item.to_dict(only=('id', 'fullname', 'email', "type")) for item in admins]
    session.close()
    return data


def put_self_admin(admin_email, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    count = 0
    admin_dict = admin.to_dict(only=('fullname', 'email'))
    keys = list(filter(lambda key: args[key] is not None and key in admin_dict and args[key] != admin_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'email':
            if session.query(Admin).filter(Admin.email == args["email"]).first():
                return raise_error("Этот email уже занят", session)[0]
            admin.email = args['email']
        if key == 'fullname':
            admin.fullname = args["fullname"]
    if "change_password" in args:
        if not admin.check_password(args["check_password"]):
            return raise_error("Пароль не совпадает с текущим паролем", session)[0]
        r, session = check_password(args['new_password'], session)
        if type(r) is dict:
            return r
        admin.set_password(args['new_password'])
        count += 1
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    fullname = admin.fullname
    session.close()
    return {"success": f"Пользователь {fullname} успешно изменён"}


def delete_self_admin(admin_email, admin_password):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]
    person = session.query(Person).get(admin.id)
    session.delete(person)
    session.delete(admin)
    session.commit()
    session.close()
    return {'success': f'Аккаунт успешно удалён'}


def create_admin(admin_email, admin_password, args):
    admin, session = check_admin(admin_email, 1)
    if type(admin) is dict:
        return admin

    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]

    if not all(args[key] is not None for key in ['fullname', 'email', "new_password"]):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания админа', session)[0]

    if session.query(Admin).filter(Admin.email == args['email']).first():
        return raise_error("Этот email уже занят", session)[0]

    res, session = check_password(args["new_password"], session)
    if type(res) is dict:
        return res

    new_admin = Admin()
    new_admin.fullname = args["fullname"]
    new_admin.email = args['email']
    new_admin.set_password(args["new_password"])
    new_admin.balance = 0
    new_admin.type = "admin"

    session.add(new_admin)
    session.commit()
    admin_id = new_admin.id
    session.close()

    return {'success': f'Админ {args["fullname"]} создан', 'id': int(admin_id)}


def get_admin(admin_email, admin_id):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    _admin = find_by_id(admin_id, session)
    if type(_admin) is dict:
        return _admin
    data = _admin.to_dict(only=('id', 'fullname', 'email', "type"))
    session.close()
    return data


def put_admin_admin(admin_email, admin_id, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin

    _admin = find_by_id(admin_id, session)
    if type(_admin) is dict:
        return _admin

    count = 0
    admin_dict = _admin.to_dict(only=('fullname', 'email'))
    keys = list(filter(lambda key: args[key] is not None and key in admin_dict and args[key] != admin_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'email':
            if session.query(Admin).filter(Admin.email == args["email"]).first():
                return raise_error("Этот email уже занят", session)[0]
            _admin.email = args['email']
        if key == 'fullname':
            _admin.fullname = args["fullname"]
    if "change_password" in args:
        if not _admin.check_password(args["check_password"]):
            return raise_error("Пароль не совпадает с текущим паролем", session)[0]
        r, session = check_password(args['new_password'], session)
        if type(r) is dict:
            return r
        _admin.set_password(args['new_password'])
        count += 1
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    fullname = _admin.fullname
    session.close()
    return {"success": f"Пользователь {fullname} успешно изменён"}


def delete_admin_admin(admin_email, admin_password, admin_id):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]

    _admin = find_by_id(admin_id, session)
    if type(_admin) is dict:
        return _admin

    fullname = _admin.fullname
    person = session.query(Person).get(admin.id)
    session.delete(person)
    session.delete(_admin)
    session.commit()
    session.close()
    return {'success': f'Админ {fullname} успешно удалён'}
