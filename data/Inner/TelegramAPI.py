from data import db_session
from data.Inner.main_file import raise_error
from data.telegram import Telegram


def find_by_id(id, session):
    telegram = session.query(Telegram).get(id)
    if not telegram:
        return raise_error(f"Бот не найден", session)
    return telegram, session


def get_telegram_by_id(telegram_id):
    session = db_session.create_session()
    telegram, session = find_by_id(telegram_id, session)
    if type(telegram) is dict:
        return telegram
    data = telegram.to_dict(only=("token", "send_to"))
    session.close()
    return data
