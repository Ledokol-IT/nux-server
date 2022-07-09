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

def run_migrations():
    options = nux.config.parse_args()
    nux.database.run_migrations(options.postgres_url)

def create_all():
    options = nux.config.parse_args()
    nux.database.create_all(options.postgres_url)


def make_migration():
    options = nux.config.parse_args()
    nux.database.make_migration(options.postgres_url)
