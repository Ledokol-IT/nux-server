import base64
import json

from loguru import logger
import firebase_admin
import firebase_admin.messaging
import firebase_admin.credentials

DISABLED = True
firebase_app = None


def setup_firebase(options):
    global firebase_app, DRY_RUN, DISABLED
    logger.info("Setup firebase start")
    if options.google_creds:
        logger.info("Setup firebase with base64 encoded string")
        creds = base64.b64decode(options.google_creds)
        creds = json.loads(creds)
        credentials = firebase_admin.credentials.Certificate(
            creds,
        )
    elif options.google_creds_file:
        logger.info(f"Setup firebase with file {options.google_creds_file}")
        credentials = firebase_admin.credentials.Certificate(
            options.google_creds_file,
        )
    else:
        logger.error(
            "Google credentials not found. Firebase will not be initialized")
        firebase_app = None
        return
    DRY_RUN = options.firebase_dry_run

    if firebase_app is None:
        firebase_app = firebase_admin.initialize_app(credentials)
        logger.info("Firebase initialized succesfuly")
    else:
        logger.info("Firebase was already initialized")
    DISABLED = False


def send_messages(
    messages: list[firebase_admin.messaging.Message],
):
    logger.debug(f"sent {len(messages)} messages")
    firebase_admin.messaging.send_all(
        messages,
        app=firebase_app,
        dry_run=DRY_RUN,
    )


def send_message(
    message: firebase_admin.messaging.Message,
):
    firebase_admin.messaging.send(
        message,
        app=firebase_app,
        dry_run=DRY_RUN,
    )
