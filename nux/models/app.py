from __future__ import annotations
import datetime
import typing as t
import uuid
from collections import defaultdict

import sqlalchemy as sa
import sqlalchemy.orm as orm
from nux.utils import now

import nux.database
import nux.models.user as muser
import nux.models.friends as mfriends
from nux.schemes import AppSchemeCreateAndroid, AppScheme


class UserInAppRecord(nux.database.Base):
    __tablename__ = "user_in_app_records"
    id: str = sa.Column(
        sa.String,
        primary_key=True,
    )  # type: ignore

    @staticmethod
    def _generate_id():
        return str(uuid.uuid4())

    user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
    )  # type: ignore
    user: 'muser.User' = orm.relationship(
        lambda: muser.User,
        back_populates="in_app_records"
    )

    app_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("apps.id"),
    )  # type: ignore
    app: 'App' = orm.relationship(lambda: App)

    dt_begin: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore
    dt_end: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
        index=True,
    )  # type: ignore


class UserInAppStatistic(nux.database.Base):
    __tablename__ = "user_in_app_statistics"
    user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore

    user: 'muser.User' = orm.relationship(
        lambda: muser.User,
        back_populates="apps_stats"
    )

    app_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("apps.id"),
        primary_key=True,
    )  # type: ignore
    app: 'App' = orm.relationship(lambda: App)

    installed: bool = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
    )  # type: ignore

    # None means never updated
    dt_stats_updated_at: datetime.datetime | None = sa.Column(
        sa.DateTime,
        nullable=True,
    )  # type: ignore

    activity_last_two_weeks: datetime.timedelta = sa.Column(
        sa.Interval,
        nullable=False,
        default=datetime.timedelta(0),
        server_default='0',
    )  # type: ignore

    activity_total: datetime.timedelta = sa.Column(
        sa.Interval,
        nullable=False,
        default=datetime.timedelta(0),
        server_default='0',
    )  # type: ignore

    dt_last_acivity: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=True,
    )  # type: ignore


class App(nux.database.Base):
    __tablename__ = "apps"

    id: str = sa.Column(
        sa.String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )  # type: ignore

    @staticmethod
    def _generate_id():
        return str(uuid.uuid4())

    android_package_name: str | None = sa.Column(
        sa.String,
        unique=True,
        nullable=True,  # maybe we will support other os
    )  # type: ignore
    name: str = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    category: str = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    icon_preview: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    image_wide: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    icon_large: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore

    approved: bool = sa.Column(
        sa.Boolean,
        nullable=False,
        server_default="FALSE",
    )  # type: ignore

    def is_visible(self):
        return "GAME" in self.category

    def __repr__(self):
        return (f"App<android_package_name={self.android_package_name}"
                f", id={self.id}>")


def create_app_android(app_data: AppSchemeCreateAndroid) -> App:
    app = App()
    app.id = App._generate_id()
    app.android_package_name = app_data.android_package_name
    app.name = app_data.name
    app.approved = False

    match_category: dict[t.Any, str] = {
        None: "OTHER",
        0: "GAME",
    }
    if app_data.android_category in match_category:
        app.category = match_category[app_data.android_category]
    else:
        app.category = "OTHER"
    return app


def determine_app_android(
        session: orm.Session,
        app_data: AppSchemeCreateAndroid
) -> tuple[bool, App]:
    """
    Return `(True, new_app)` if no mathed app is found,
    returns `(False, found_app)` otherwise.
    App is added to session, but not commited
    """
    app = session.query(App).filter(
        App.android_package_name == app_data.android_package_name
    ).first()
    if app is not None:
        return False, app

    app = create_app_android(app_data)
    session.add(app)
    return True, app


def add_app_to_user(
        session: orm.Session,
        user: 'muser.User',
        app: App,
):
    app_stats = session.query(UserInAppStatistic).get({
        "user_id": user.id,
        "app_id": app.id,
    })
    if app_stats is None:
        app_stats = UserInAppStatistic()
        app_stats.app = app
        app_stats.user = user
        session.add(app_stats)
    app_stats.installed = True


def delete_app_from_user(
        session: orm.Session,
        user: 'muser.User',
        app: App,
):
    app_stats = session.query(UserInAppStatistic).get({
        "user_id": user.id,
        "app_id": app.id,
    })
    if app_stats is None:
        return
    app_stats.installed = False


def apply_visible(q: orm.Query) -> orm.Query:
    return q.where(App.category.contains('GAME'))  # type: ignore


def get_user_apps(
        session: orm.Session,
        user: muser.User,
        *,
        only_visible: bool = False,
        only_installed: bool = True,
) -> list[App]:
    q = (
        session.query(App)
        .join(UserInAppStatistic)
        .where(UserInAppStatistic.user_id == user.id)
    )
    if only_visible:
        q = apply_visible(q)
    if only_installed:
        q = q.where(UserInAppStatistic.installed)

    return q.all()


class AppAndUserStatistics(t.NamedTuple):
    app: App
    statistics: UserInAppStatistic


def get_user_apps_and_stats(
        session: orm.Session,
        user: muser.User,
        *,
        only_visible: bool = False,
        only_installed: bool = True,
) -> list[AppAndUserStatistics]:
    q = (
        session.query(App, UserInAppStatistic)
        .join(UserInAppStatistic)
        .where(UserInAppStatistic.user_id == user.id)
    )
    if only_visible:
        q = apply_visible(q)
    if only_installed:
        q = q.where(UserInAppStatistic.installed)

    return list(map(AppAndUserStatistics._make, q.all()))


def set_apps_to_user(
        session: orm.Session,
        user: 'muser.User',
        apps: t.Iterable[App],
):
    user_apps = set(get_user_apps(session, user))
    apps = set(apps)
    to_add = apps.difference(user_apps)
    to_delete = user_apps.difference(apps)
    for app in to_add:
        add_app_to_user(session, user, app)
    for app in to_delete:
        delete_app_from_user(session, user, app)


def get_app(
        session: orm.Session,
        id: str | None = None, android_package_name: str | None = None
) -> App | None:
    cnt_args = sum(map(lambda x: x is not None, [id, android_package_name]))
    if cnt_args != 1:
        raise ValueError(f"Expected 1 argument. Find {cnt_args}")

    query = session.query(App)
    app = None
    if id is not None:
        app = query.get(id)
    elif android_package_name is not None:
        app = query.filter(App.android_package_name
                           == android_package_name).first()
    return app


def get_recommended_apps(
        session: orm.Session,
        user: muser.User,
) -> list[App]:
    friends = mfriends.get_friends(session, user, limit=100)
    recommended: defaultdict[App, int] = defaultdict(lambda: 0)
    for friend in friends:
        for app in get_user_apps(session, friend, only_visible=True):
            recommended[app] += 1
    for app in get_user_apps(session, user, only_visible=True):
        recommended.pop(app, None)
    recommended_list = sorted(recommended.items(), key=lambda t: t[1],
                              reverse=True)
    return [app for app, _ in recommended_list]


def add_user_in_app_record(
        session: orm.Session,
        user: muser.User,
        app: App,
        dt_begin: datetime.datetime,
        dt_end: datetime.datetime,
):
    assert dt_begin < dt_end
    record = UserInAppRecord()
    record.id = record._generate_id()
    record.user = user
    record.app = app
    record.dt_begin = dt_begin
    record.dt_end = dt_end
    session.add(record)
    return record


def update_periodic_stats(
        session: orm.Session,
        user: muser.User,
):
    TWO_WEEKS = datetime.timedelta(days=14)
    two_weeks_before_now = now() - TWO_WEEKS
    stats: dict[App, UserInAppStatistic] = {}
    for record in user.in_app_records:
        if record.dt_end < two_weeks_before_now:
            session.delete(record)
            continue
        if record.app not in stats:
            stat = stats[record.app] = session.query(UserInAppStatistic).get(
                {"user_id": user.id, "app_id": record.app.id})
            if stat is None:
                continue
            stat.dt_stats_updated_at = now()
            stat.activity_last_two_weeks = datetime.timedelta(0)
        else:
            stat = stats[record.app]
        stat.activity_last_two_weeks += record.dt_end - \
            max(record.dt_begin, two_weeks_before_now)
        print(record.dt_begin, two_weeks_before_now)
        if stat.dt_last_acivity is None:
            stat.dt_last_acivity = record.dt_end
        else:
            stat.dt_last_acivity = max(
                stats[record.app].dt_last_acivity, record.dt_end)
