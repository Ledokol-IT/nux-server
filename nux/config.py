import os
import configargparse
import argparse

SECRET_KEY: str


def add_data_base_args(p: configargparse.ArgParser):
    p.add_argument("--pg-user", env_var="POSTGRES_USER", required=True)
    p.add_argument("--pg-password", env_var="POSTGRES_PASSWORD", required=True)
    p.add_argument("--pg-host", env_var="POSTGRES_HOST", required=True)
    p.add_argument("--pg-db", env_var="POSTGRES_DB", required=True)
    return p


def add_s3_options(p: configargparse.ArgParser):
    p.add_argument("--aws-access-key-id", env_var="AWS_ACCESS_KEY_ID")
    p.add_argument("--aws-secret-access-key", env_var="AWS_SECRET_ACCESS_KEY")
    return p


def get_pg_url(options: configargparse.Namespace):
    postgres_url = (
        "postgresql://"
        "%(pg_user)s:%(pg_password)s"
        "@%(pg_host)s/%(pg_db)s" % options.__dict__
    )
    return postgres_url


def init_arg_parser():
    p = configargparse.ArgParser(
        ignore_unknown_config_file_keys=True,
    )
    return p


def parse_args_from_parser(
    p: configargparse.ArgParser,
    args=None
) -> argparse.Namespace:
    return p.parse_known_args(args)[0]


def parse_args(args=None):
    global SECRET_KEY, PORT
    p = init_arg_parser()
    add_data_base_args(p)
    add_s3_options(p)
    p.add_argument("--secret-key", env_var="NUX_SECRET_KEY", required=True)
    p.add_argument("--port", default=8000, env_var="NUX_PORT", type=int)
    p.add_argument("--google-creds-file",
                   env_var="GOOGLE_CREDS_FILE",
                   default="google_creds.json")
    p.add_argument("--google-creds",
                   env_var="GOOGLE_CREDS",)
    p.add_argument("--firebase-dry-run", action="store_true")

    options = parse_args_from_parser(p, args)
    options.postgres_url = get_pg_url(options)

    os.environ["NUX_SECRET_KEY"] = ""

    SECRET_KEY = options.secret_key

    return options
