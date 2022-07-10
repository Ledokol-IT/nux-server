import fastapi

from nux.auth import auth_router
import nux.config
import nux.database
import nux.events
import nux.firebase
import nux.notifications
from nux.resources.apps_resources import apps_router
from nux.resources.status_resources import status_router
from nux.resources.users_resources import user_router


def create_app(options):
    """Create and setup fastapi app ready to run."""
    app = fastapi.FastAPI(
        title="NUX (Ledokol)"
    )
    nux.database.connect_to_db(options.postgres_url)
    nux.firebase.setup_firebase(options)
    nux.notifications.setup_notifications(options)

    @app.get("/")
    def index():
        return {"hello": "world"}

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(status_router)
    app.include_router(apps_router)

    return app
