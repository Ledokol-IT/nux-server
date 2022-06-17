import typing as t

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import fastapi


Base = sqlalchemy.orm.declarative_base()


def session_generator() -> t.Generator[sqlalchemy.orm.Session, None, None]:
    print("Generate session")
    with Session() as session:
        yield session


def SessionDependecy() -> sqlalchemy.orm.Session:
    return fastapi.Depends(session_generator, use_cache=True)

def connect_to_db(options):
    global Session, engine
    engine = sqlalchemy.create_engine(options.postgres_url)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)



def create_all(options):
    connect_to_db(options)
    import nux.models.user as _
    import nux.models.status as _
    import nux.models.app as _

    Base.metadata.create_all(engine)

    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    # from alembic.config import Config
    # from alembic import command
    # alembic_cfg = Config("./alembic.ini")
    # alembic_cfg.set_main_option('sqlalchemy.url', options.postgres_url)
    # command.stamp(alembic_cfg, "head")
