import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'product'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    link = sqlalchemy.Column(sqlalchemy.String)
    max_discount = sqlalchemy.Column(sqlalchemy.Integer)
    bad_count = sqlalchemy.Column(sqlalchemy.Integer)
    bad_price = sqlalchemy.Column(sqlalchemy.Integer)
    good_count = sqlalchemy.Column(sqlalchemy.Integer)
    good_price = sqlalchemy.Column(sqlalchemy.Integer)
    in_stoke = sqlalchemy.Column(sqlalchemy.Boolean)
    image = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    specifications = sqlalchemy.Column(sqlalchemy.String)

    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("category.id"))
    category = orm.relation('Category')

    def __repr__(self):
        return f'<Product> Товар {self.id}'
