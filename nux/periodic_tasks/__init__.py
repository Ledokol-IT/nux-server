import ischedule
from loguru import logger

import nux.database
import nux.firebase
from nux.periodic_tasks._clear_statuses import clear_statuses, ping_users


def run_tasks(postgres_url, options):
    logger.info("Connecting to db...")
    nux.database.connect_to_db(postgres_url)
    nux.firebase.setup_firebase(options)

    logger.info("Start tasks.\n"
                "Ctrl+C to stop.")
    ischedule.schedule(clear_statuses, interval=10)
    ischedule.schedule(ping_users, interval=10)

    try:
        ischedule.run_loop()
    except KeyboardInterrupt:
        logger.info("Stopped by user")


__all__ = (
    'run_tasks',
)
