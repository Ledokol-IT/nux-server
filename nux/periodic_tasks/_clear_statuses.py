import logging
import typing as t

import ischedule

import nux.config
import nux.database
import nux.models.status

logger = logging.getLogger(__name__)


def clear_statuses(postgres_url, seconds=10):
    logger.info("Connecting to db...")
    nux.database.connect_to_db(postgres_url)

    def task():
        logger.debug("run clear_statuses")
        with nux.database.Session() as session:
            nux.models.status.clear_offline_users_by_ttl(session)
            session.commit()
        logger.debug("finish clear_statuses")

    logger.info("Start clearing statuses.\n"
                "Ctrl+C to stop.")
    ischedule.schedule(task, interval=seconds)

    try:
        ischedule.run_loop()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
