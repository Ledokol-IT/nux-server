import logging

import firebase_admin
import firebase_admin.messaging
import firebase_admin.credentials

logger = logging.getLogger(__name__)


def setup_firebase(options):
    global firebase_app, DRY_RUN

    if options.google_creds is None:
        logger.error(
            "Google credentials not found. Firebase will not be initialized")
        firebase_app = None
        return

    credentials = firebase_admin.credentials.Certificate(
        options.google_creds,
    )
    DRY_RUN = options.firebase_dry_run

    firebase_app = firebase_admin.initialize_app(credentials)


def send_messages(
    messages: list[firebase_admin.messaging.Message],
):
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
