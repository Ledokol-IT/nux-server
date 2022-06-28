import uvicorn

from nux.app import create_app
import nux.database

import nux.config

def run_app():
    options = nux.config.parse_args()
    uvicorn.run(
        create_app(options=options),  # type: ignore
        port=nux.config.PORT,
        host="0.0.0.0"
    )

def create_all():
    options = nux.config.parse_args()
    nux.database.create_all(options)

