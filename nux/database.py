import typing as t

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import fastapi

from nux.config import options

CONN_STR = "postgresql://%(pg_user)s:%(pg_password)s@%(pg_host)s/%(pg_db)s" % options.__dict__

engine = sqlalchemy.create_engine(CONN_STR)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

Base = sqlalchemy.ext.declarative.declarative_base()


def session_generator() -> t.Generator[sqlalchemy.orm.Session, None, None]:
    print("Generate session")
    with Session() as session:
        yield session

def SessionDependecy() -> sqlalchemy.orm.Session:
    return fastapi.Depends(session_generator, use_cache=True)


