import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'order'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tik_id = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'<Order> заказ {self.id}'
