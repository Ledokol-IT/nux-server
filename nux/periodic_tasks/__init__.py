import logging

import ischedule

import nux.database
from nux.periodic_tasks._clear_statuses import clear_statuses, ping_users

logger = logging.getLogger(__name__)


def run_tasks(postgres_url):
    logger.info("Connecting to db...")
    nux.database.connect_to_db(postgres_url)

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
