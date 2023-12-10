from pydantic import config
import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from database.database_scheme import create_metadata

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return

    conn_str = f'postgresql://{"admin"}:{"admin"}@{"194.58.111.234"}:{"5432"}/{"tour_agency"}'
    print(f'Connected to database {conn_str}')

    engine = sa.create_engine(conn_str)
    #Следующие две строчки нужно раскомментировать, только если вы хотите создать пустую базу данных
    metadata = create_metadata()
    metadata.create_all(engine)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()

