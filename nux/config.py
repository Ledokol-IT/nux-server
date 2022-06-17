import os
import configargparse
import argparse

SECRET_KEY: str
PORT: str

def parse_args(args=None):
    global SECRET_KEY, PORT
    p = configargparse.ArgParser(ignore_unknown_config_file_keys=True)
    p.add_argument("--pg-user", env_var="POSTGRES_USER", required=True)
    p.add_argument("--pg-password", env_var="POSTGRES_PASSWORD", required=True)
    p.add_argument("--pg-host", env_var="POSTGRES_HOST", required=True)
    p.add_argument("--pg-db", env_var="POSTGRES_DB", required=True)
    p.add_argument("--secret-key", env_var="NUX_SECRET_KEY", required=True)
    p.add_argument("--port", default=8000, env_var="NUX_PORT", type=int)

    options: argparse.Namespace = p.parse_known_args(args)[0]

    os.environ["NUX_SECRET_KEY"] = ""

    options.postgres_url = "postgresql://%(pg_user)s:%(pg_password)s@%(pg_host)s/%(pg_db)s" % options.__dict__

    SECRET_KEY = options.secret_key
    PORT = options.port

    return options

