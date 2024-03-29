from nux.config import add_firebase_options


def run_app():
    import uvicorn

    import nux.config
    import nux.database
    from nux.app import create_app

    options = nux.config.parse_args()

    uvicorn.run(
        create_app(options=options),  # type: ignore
        port=options.port,
        host="0.0.0.0",
        access_log=False,
    )


def print_shit():
    import nux.database
    from nux.config import add_data_base_args,\
        parse_args_from_parser, init_arg_parser
    from nux.models.app import App

    p = add_data_base_args(init_arg_parser())
    o = parse_args_from_parser(p)
    nux.database.create_all(o.postgres_url)
    nux.database.connect_to_db(o.postgres_url)
    s = nux.database.Session()
    apps = s.query(App).where(App.approved).all()
    for app in apps:
        print(app.name, app.category)


def run_db_tasks():
    import nux.config
    import nux.periodic_tasks

    p = nux.config.add_data_base_args(nux.config.init_arg_parser())
    add_firebase_options(p)
    options = nux.config.parse_args_from_parser(p)
    nux.periodic_tasks.run_tasks(options.postgres_url, options)


def run_migrations():
    import nux.database
    import nux.config

    p = nux.config.add_data_base_args(nux.config.init_arg_parser())
    add_firebase_options(p)
    options = nux.config.parse_args_from_parser(p)
    nux.database.run_migrations(options.postgres_url)


def run_icons_updater():
    import nux.config
    import nux.icons_updater

    p = nux.config.add_data_base_args(nux.config.init_arg_parser())
    add_firebase_options(p)
    options = nux.config.parse_args_from_parser(p)
    nux.icons_updater.run_updater(options.postgres_url)


def update_all_icons():
    import nux.config
    import nux.icons_updater

    p = nux.config.add_data_base_args(nux.config.init_arg_parser())
    add_firebase_options(p)
    options = nux.config.parse_args_from_parser(p)
    nux.icons_updater.update_all(options.postgres_url)


def create_debug_session():
    import nux.config
    import nux.database

    p = nux.config.add_data_base_args(nux.config.init_arg_parser())
    options = nux.config.parse_args_from_parser(p)
    nux.database.connect_to_db(postgres_url=options.postgres_url)
    return nux.database.Session()


def create_all():
    import nux.database
    import nux.config

    options = nux.config.parse_args()
    nux.database.create_all(options.postgres_url)


def make_migration():
    import nux.database
    import nux.config

    options = nux.config.parse_args()
    nux.database.make_migration(options.postgres_url)


def delete_user():
    import nux.config
    import nux.database
    from nux.models.user import get_user

    p = nux.config.add_data_base_args(nux.config.init_arg_parser())
    p.add_argument("--phone")
    p.add_argument("--nickname")
    p.add_argument("--id")
    options = nux.config.parse_args_from_parser(p)
    nux.database.connect_to_db(options.postgres_url)
    with nux.database.Session() as session:
        u = get_user(
            session,
            phone=options.phone,
            id=options.id,
            nickname=options.nickname
        )
        session.delete(u)
        session.commit()


def alembic():
    import alembic.config

    import nux.config
    import nux.database

    alembic_cmd = alembic.config.CommandLine()
    alembic_options = alembic_cmd.parser.parse_args()
    options = nux.config.parse_args()
    alembic_cfg = nux.database.make_alembic_config(options.postgres_url)
    alembic_cmd.run_cmd(alembic_cfg, alembic_options)
