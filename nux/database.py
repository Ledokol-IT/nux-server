import typing as t

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import fastapi


Base = sqlalchemy.orm.declarative_base()


def Session() -> sqlalchemy.orm.Session:
    return _Session()


def session_generator() -> t.Generator[sqlalchemy.orm.Session, None, None]:
    with Session() as session:
        yield session


def SessionDependecy() -> sqlalchemy.orm.Session:
    return fastapi.Depends(session_generator, use_cache=True)


def connect_to_db(postgres_url: str):
    global _Session, engine
    engine = sqlalchemy.create_engine(postgres_url)
    _Session = sqlalchemy.orm.sessionmaker(bind=engine)


def make_alembic_config(postgres_url):
    import alembic.config
    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    alembic_cfg = alembic.config.Config("./alembic.ini")
    alembic_cfg.set_main_option('sqlalchemy.url', postgres_url)
    return alembic_cfg


def create_all(postgres_url: str):
    import nux.models.user as _
    import nux.models.status as _
    import nux.models.app as _
    import nux.models.friends as _
    import nux.confirmation as _
    import nux.periodic_tasks._clear_statuses as _

    connect_to_db(postgres_url)

    Base.metadata.create_all(engine)

    import alembic.command
    import alembic.config

    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    alembic_cfg = make_alembic_config(postgres_url)
    alembic.command.stamp(alembic_cfg, "head")


def run_migrations(postgres_url: str):
    import alembic.command
    import alembic.config

    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    alembic_cfg = make_alembic_config(postgres_url)
    alembic.command.upgrade(alembic_cfg, "head")


def make_migration(postgres_url: str):
    import alembic.command
    import alembic.config

    import nux.models.user as _
    import nux.models.status as _
    import nux.models.app as _
    import nux.models.friends as _
    import nux.confirmation as _
    import nux.periodic_tasks._clear_statuses as _

    migration_message = input("Enter message for migration: ")

    alembic_cfg = make_alembic_config(postgres_url)
    alembic.command.revision(
        alembic_cfg,
        message=migration_message,
        autogenerate=True,
    )
