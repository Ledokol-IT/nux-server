from loguru import logger
import time

import requests
from bs4 import BeautifulSoup
from sqlalchemy import log
from sqlalchemy.orm import Query
import ischedule

import nux.models.app as mapp
import nux.database


def get_link_icon(package: str) -> None | str:
    url = f'https://play.google.com/store/apps/details?id={package}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'}  # noqa
    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        logger.exception(e)
        return None
    soup = BeautifulSoup(response.text, "lxml")

    img_list = soup.find_all("img", alt="Icon image")
    if not img_list:
        return None

    url: str = img_list[0]["src"]
    if not url.startswith("https://"):
        logger.warning("Bad image. Dont starts with https")
        return None
    if "fonts" in url:
        logger.warning("Bad image. Contains fonts")
        return None
    return url


def update_icon(app: mapp.App) -> bool:
    if app.android_package_name is None:
        return True
    url = get_link_icon(app.android_package_name)
    if url is None:
        return False
    app.icon_preview = url
    logger.info("Update for App<android_package_name={}>.icon_preview={}",
                app.android_package_name, app.icon_preview)
    return True


def update_icons_batch(batch_size=10):
    session = nux.database.Session()
    with session.begin():
        query = session.query(mapp.App)
        query: Query[mapp.App] = query.where(
            mapp.App.icon_preview.is_(None))  # type: ignore
        apps = query.limit(batch_size).all()
        if not apps:
            logger.info("No apps without icon found")
        for app in apps:
            if not update_icon(app):
                time.sleep(10)


def update_all(postgres_url):
    nux.database.connect_to_db(postgres_url)
    session = nux.database.Session()
    with session.begin():
        query = session.query(mapp.App)
        apps = query.yield_per(100)
        for app in apps:
            if not update_icon(app):
                time.sleep(10)


def run_updater(postgres_url):
    logger.info("Connecting to db...")
    nux.database.connect_to_db(postgres_url)

    logger.info("Start tasks.\n"
                "Ctrl+C to stop.")
    ischedule.schedule(update_icons_batch, interval=5)

    try:
        ischedule.run_loop()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
