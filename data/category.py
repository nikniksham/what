import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    father = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pra_father = sqlalchemy.Column(sqlalchemy.String)
    link = sqlalchemy.Column(sqlalchemy.String)

    product = orm.relation('Product')

    def __repr__(self):
        return f'<Category> Категория {self.id}'
