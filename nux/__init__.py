import uvicorn

from nux.app import create_app
import nux.database

import nux.config


def run_app():
    options = nux.config.parse_args()
    uvicorn.run(
        create_app(options=options),  # type: ignore
        port=options.port,
        host="0.0.0.0"
    )


def print_shit():
    from nux.s3 import setup_s3, print_shit
    p = nux.config.add_s3_options(nux.config.init_arg_parser())
    options = nux.config.parse_args_from_parser(p)
    setup_s3(options.aws_access_key_id, options.aws_secret_access_key)
    print_shit()


def run_clear_status():
    import nux.config
    import nux.periodic_tasks
    p = nux.config.add_data_base_args(nux.config.init_arg_parser())
    options = nux.config.parse_args_from_parser(p)
    nux.periodic_tasks.clear_statuses(options.postgres_url)
        


def run_migrations():
    options = nux.config.parse_args()
    nux.database.run_migrations(options.postgres_url)


def create_all():
    options = nux.config.parse_args()
    nux.database.create_all(options.postgres_url)


def make_migration():
    options = nux.config.parse_args()
    nux.database.make_migration(options.postgres_url)


def alembic():
    import alembic.config

    alembic_cmd = alembic.config.CommandLine()
    alembic_options = alembic_cmd.parser.parse_args()
    options = nux.config.parse_args()
    alembic_cfg = nux.database.make_alembic_config(options.postgres_url)
    alembic_cmd.run_cmd(alembic_cfg, alembic_options)
