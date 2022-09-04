import logging
import time

import fastapi
from loguru import logger

from nux.auth import auth_router
import nux.config
import nux.confirmation
import nux.database
import nux.default_profile_pics
import nux.default_profile_pics
import nux.events
import nux.firebase
from nux.resources.apps_resources import apps_router
import nux.resources.friends_resources
from nux.resources.status_resources import status_router
from nux.resources.users_resources import user_router
import nux.s3
import nux.sms


def format_client(p):
    return f"{p[0]}:{p[1]}"


async def log_requests(request: fastapi.Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(e)
        process_time = (time.time() - start_time)
        logger.error(
            f"{request.url} {500} {format_client(request.client)} {process_time:.5f}sec")
        raise e

    level = "INFO"
    if 400 <= response.status_code:
        level = logging.WARNING
    if 500 <= response.status_code:
        level = logging.ERROR

    process_time = (time.time() - start_time)

    logger.log(
        level, f"{request.url} {response.status_code} {format_client(request.client)} {process_time:.5f}sec")

    return response


def create_app(options):
    """Create and setup fastapi app ready to run."""
    app = fastapi.FastAPI(
        title="NUX (Ledokol)",
    )
    app.middleware("http")(log_requests)

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

    @app.get("/error")
    def error():
        raise ValueError

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(status_router)
    app.include_router(apps_router)
    app.include_router(nux.resources.friends_resources.router)
    app.include_router(nux.confirmation.confirmation_router)
    app.include_router(nux.default_profile_pics.router)

    return app
