import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Telegram(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'telegram'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    token = sqlalchemy.Column(sqlalchemy.String)
    send_to = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'<Telegram> телеграм бот {self.id}'
