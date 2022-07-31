import sqlalchemy
from data.person import Person


class Admin(Person):
    __tablename__ = 'admin'
    id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('person.id'), primary_key=True)

    def __repr__(self):
        return f'<Admin> Админ {self.id} {self.fullname}'
