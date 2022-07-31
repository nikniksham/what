import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Ticket(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'ticket'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    price = sqlalchemy.Column(sqlalchemy.String)
    is_block = sqlalchemy.Column(sqlalchemy.Boolean)

    person_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("person.id"))
    person = orm.relation('Person')

    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("product.id"))
    product = orm.relation('Product')

    def __repr__(self):
        return f'<Ticket> Заявка {self.id}'
