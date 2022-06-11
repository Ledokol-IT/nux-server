import typing as t

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import fastapi

from nux.config import options

CONN_STR = "postgresql://%(pg_user)s:%(pg_password)s@%(pg_host)s/%(pg_db)s" % options.__dict__
print(CONN_STR)

engine = sqlalchemy.create_engine(CONN_STR)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

Base = sqlalchemy.orm.declarative_base()


def session_generator() -> t.Generator[sqlalchemy.orm.Session, None, None]:
    print("Generate session")
    with Session() as session:
        yield session


def SessionDependecy() -> sqlalchemy.orm.Session:
    return fastapi.Depends(session_generator, use_cache=True)


def create_all():
    Base.metadata.create_all(engine)

    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config("./alembic.ini")
    alembic_cfg.set_main_option('sqlalchemy.url', CONN_STR)
    command.stamp(alembic_cfg, "head")
