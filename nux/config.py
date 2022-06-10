import os
import configargparse
import argparse

p = configargparse.ArgParser()
p.add_argument("--pg-user", env_var="POSTGRES_USER", required=True)
p.add_argument("--pg-password", env_var="POSTGRES_PASSWORD", required=True)
p.add_argument("--pg-host", env_var="POSTGRES_HOST", required=True)
p.add_argument("--pg-db", env_var="POSTGRES_DB", required=True)
p.add_argument("--secret-key", env_var="NUX_SECRET_KEY", required=True)
p.add_argument("--port", default=8000, env_var="NUX_PORT", type=int)

options: argparse.Namespace = p.parse_args()

os.environ["NUX_SECRET_KEY"] = ""

