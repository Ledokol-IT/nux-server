import fastapi
from nux.resources.auth import auth_router


def create_app():
    """Create and setup fastapi app ready to run."""
    app = fastapi.FastAPI()
    @app.get("/")
    def index():
        return {"hello": "world"}
    app.include_router(auth_router)
    return app
