import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Integer, Text, Column
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_session import SqlAlchemyBase


class TourOperator(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tour_operators'
    __table_args__ = {'extend_existing': True}

    id = sqlalchemy.Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', Text, nullable=False)
    description = Column('description', Text, nullable=False)
    telephone = Column('telephone', Text, nullable=False)
    email = Column('email', Text, nullable=False)
    password = Column('password', Text, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_parameter(self, type, new_value):
        if type == "name":
            self.name = new_value
        elif type == "description":
            self.description = new_value
        elif type == "telephone":
            self.telephone = new_value
        elif type == "email":
            self.email = new_value
        elif type == "password":
            self.set_password(new_value)
