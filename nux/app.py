import logging

import fastapi

from nux.auth import auth_router
import nux.config
import nux.confirmation
import nux.database
import nux.default_profile_pics
import nux.events
import nux.firebase
import nux.default_profile_pics
from nux.resources.apps_resources import apps_router
from nux.resources.status_resources import status_router
from nux.resources.users_resources import user_router
import nux.resources.friends_resources
import nux.s3
import nux.sms


def create_app(options):
    """Create and setup fastapi app ready to run."""
    app = fastapi.FastAPI(
        title="NUX (Ledokol)"
    )
    print(options.logging_level)
    logging.basicConfig(level=options.logging_level)
    nux.database.connect_to_db(options.postgres_url)
    nux.firebase.setup_firebase(options)
    if not options.aws_disable:
        nux.s3.setup_s3(
            options.aws_access_key_id,
            options.aws_secret_access_key
        )
    nux.default_profile_pics.setup()
    if not options.sms_disable:
        nux.sms.setup_sms(options.smsaero_email, options.smsaero_apikey)

    @app.get("/")
    def index():
        return {"hello": "world"}

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(status_router)
    app.include_router(apps_router)
    app.include_router(nux.resources.friends_resources.router)
    app.include_router(nux.confirmation.confirmation_router)
    app.include_router(nux.default_profile_pics.router)

    return app
