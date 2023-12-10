import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Integer, Text, Column, JSON, Date, ForeignKey, ARRAY

from database.db_session import SqlAlchemyBase


class Tour(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tours'
    __table_args__ = {'extend_existing': True}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', Text, nullable=False)
    season_price = Column('season_price', JSON, nullable=False)
    dates = Column('dates', ARRAY(Date), nullable=False)
    description = Column('description', Text, nullable=False)
    place = Column('place', JSON, nullable=False)
    duration = Column('duration', Text, nullable=False)
    limit = Column('limit', Integer, nullable=False)
    id_operator = Column('id_operator', Integer, ForeignKey("tour_operators.id"))

    def set_parameter(self, type, new_value):
        if type == "name":
            self.name = new_value
        elif type == "season_price":
            self.season_price = new_value
        elif type == "dates":
            self.dates = new_value
        elif type == "description":
            self.description = new_value
        elif type == "place":
            self.place = new_value
        elif type == "duration":
            self.duration = new_value
        elif type == "limit":
            self.limit = new_value
