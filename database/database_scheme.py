from sqlalchemy import MetaData, Table, Column, Integer, String, Text, ForeignKey, JSON, Date, ARRAY


def create_metadata():
    metadata = MetaData()

    tour_operator = Table('tour_operators', metadata,
                          Column('id', Integer(), primary_key=True, autoincrement=True),
                          Column('name', Text(), nullable=False),
                          Column('description', Text(), nullable=False),
                          Column('telephone', Text(), nullable=False),
                          Column('email', Text(), nullable=False),
                          Column('password', Text(), nullable=False),
                          )

    tour = Table('tours', metadata,
                 Column('id', Integer(), primary_key=True, autoincrement=True),
                 Column('name', Text(), nullable=False),
                 Column('season_price', JSON(), nullable=False),
                 Column('dates', ARRAY(Date), nullable=False),
                 Column('description', Text(), nullable=False),
                 Column('place', JSON(), nullable=False),
                 Column('duration', Text(), nullable=False),
                 Column('limit', Integer(), nullable=False),
                 Column('bonus', Integer(), nullable=False),
                 Column('id_operator', Integer(), ForeignKey("tour_operators.id")),
                 )

    client = Table("clients", metadata,
                   Column('id', Integer(), primary_key=True, autoincrement=True),
                   Column('name', Text(), nullable=False),
                   Column('type', Text(), nullable=False),
                   Column('telephone', Text(), nullable=False),
                   Column('email', Text(), nullable=False),
                   Column('password', Text(), nullable=False),
                   )

    booking = Table('bookings', metadata,
                    Column("id", Integer(), primary_key=True, autoincrement=True),
                    Column('id_client', Integer(), ForeignKey("clients.id")),
                    Column('id_tour', Integer(), ForeignKey("tours.id")),
                    Column('date', Date(), nullable=False),
                    Column('count', Integer(), nullable=False)
                    )

    bonus = Table("bonus", metadata,
                  Column("id", Integer(), primary_key=True, autoincrement=True),
                  Column('id_client', Integer(), ForeignKey("clients.id")),
                  Column('id_operator', Integer(), ForeignKey("tour_operators.id")),
                  Column('count', Integer(), nullable=False),
                  )

    return metadata
