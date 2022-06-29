import fastapi

from nux.auth import auth_router
from nux.resources.users_resources import user_router
from nux.resources.status_resources import status_router
from nux.resources.apps_resources import apps_router
import nux.database
import nux.config


def create_app(options):
    """Create and setup fastapi app ready to run."""
    app = fastapi.FastAPI()
    nux.database.connect_to_db(options)

    @app.get("/")
    def index():
        return {"hello": "world"}

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(status_router)
    app.include_router(apps_router)
    return app
