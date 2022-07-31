import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Person(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'person'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    fullname = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String)
    balance = sqlalchemy.Column(sqlalchemy.Integer)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)

    type = sqlalchemy.Column(sqlalchemy.String)

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    ticket = orm.relation('Ticket')

    def __repr__(self):
        return f'<Person> {self.id} Базовый юзер {self.fullname}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
