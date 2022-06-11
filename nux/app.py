import fastapi

from nux.auth import auth_router
from nux.resources.users_resources import user_router


def create_app():
    """Create and setup fastapi app ready to run."""
    app = fastapi.FastAPI()

    @app.get("/")
    def index():
        return {"hello": "world"}

    app.include_router(auth_router)
    app.include_router(user_router)
    return app
