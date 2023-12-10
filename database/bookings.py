import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Integer, Text, Column, JSON, Date, ForeignKey

from database.db_session import SqlAlchemyBase


class Booking(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'bookings'
    __table_args__ = {'extend_existing': True}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    id_client = Column('id_client', Integer, ForeignKey("clients.id"))
    id_tour = Column('id_tour', Integer, ForeignKey("tours.id"))
    date = Column('date', Date, nullable=False)
    count = Column('count', Integer, nullable=False)
