from data.admin import Admin
from data import db_session
from data.person import Person


def raise_error(error, session=None):
    if session:
        session.close()
    return {"error": error}, 1


def check_admin(email):
    session = db_session.create_session()
    user = session.query(Admin).filter(Admin.email == email).first()
    if not user:
        return raise_error(f"Админ {email} не найден", session)[0]
    return user, session


def check_person(email):
    session = db_session.create_session()
    user = session.query(Person).filter(Person.email == email).first()
    if not user:
        return raise_error(f"Аккаунт {email} не найден", session)[0]
    return user, session


def check_password(password, session):
    errors = {0: 'Пароль должен быть в длину 8 или более символов', 1: 'Пароль должен содержать хотя бы 1 букву',
              2: 'Пароль должен содержать хотя бы 1 цифру'}
    if not len(password) >= 8:
        return raise_error(errors[0], session)
    if password.isdigit():
        return raise_error(errors[1], session)
    if password.isalpha():
        return raise_error(errors[2], session)
    return True, session
