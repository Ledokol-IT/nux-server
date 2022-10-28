import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Query
import ischedule
import logging

import nux.models.app as mapp
import nux.database

logger = logging.getLogger(__name__)


def get_link_icon(package: str):
    url = f'https://play.google.com/store/apps/details?id={package}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    img_list = soup.find_all("img")
    if(len(img_list) == 0):
        return None

    return img_list[0]["src"]


def update_icon(app: mapp.App):
    if app.android_package_name is None:
        return
    app.icon_preview = get_link_icon(app.android_package_name)
    logger.info(f"Update for App<android_package_name=%s>.icon_preview=%s",
                app.android_package_name, app.icon_preview)


def update_icons_batch(batch_size=10):
    with nux.database.Session() as session:
        query = session.query(mapp.App)
        query: Query[mapp.App] = query.where(
            mapp.App.icon_preview.is_(None))  # type: ignore
        apps = query.limit(batch_size).all()
        for app in apps:
            update_icon(app)
        session.commit()


def run_updater(postgres_url):
    logger.info("Connecting to db...")
    nux.database.connect_to_db(postgres_url)

    logger.info("Start tasks.\n"
                "Ctrl+C to stop.")
    ischedule.schedule(update_icons_batch, interval=10)

    try:
        ischedule.run_loop()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
