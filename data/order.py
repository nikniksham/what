import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'order'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    status = sqlalchemy.Column(sqlalchemy.Integer)
    max = sqlalchemy.Column(sqlalchemy.Integer)
    current = sqlalchemy.Column(sqlalchemy.Integer)
    prod_id = sqlalchemy.Column(sqlalchemy.Integer)
    info = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'<Order> заказ {self.id}'
