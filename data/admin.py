import sqlalchemy
from sqlalchemy import case
from data.person import Person


class Admin(Person):
    __tablename__ = 'admin'
    id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('person.id'), primary_key=True)

    user_type = sqlalchemy.Column(sqlalchemy.String)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
        "polymorphic_on": case(
            [
                (user_type == "user", "user"),
            ],
            else_="user"
        )
    }

    def __repr__(self):
        return f'<Admin> Админ {self.id} {self.fullname}'
