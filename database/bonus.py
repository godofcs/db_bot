import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Integer, Text, Column, JSON, Date, ForeignKey

from database.db_session import SqlAlchemyBase


class Bonus(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'bonus'
    __table_args__ = {'extend_existing': True}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    id_client = Column('id_client', Integer, ForeignKey("clients.id"))
    id_operator = Column('id_operator', Integer, ForeignKey("tour_operators.id"))
    count = Column('count', Integer, nullable=False)
