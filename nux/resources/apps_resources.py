from __future__ import annotations

import datetime

import fastapi
import pydantic
import sqlalchemy.orm

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
import nux.models.app as mapp
import nux.models.user as muser
import nux.s3

from nux.schemes import AppAndUserStatisticsScheme, AppScheme


apps_router = fastapi.APIRouter()


class SyncInstalledAppsResponse(pydantic.BaseModel):
    apps: list[AppScheme]
    send_icons_apps_ids: list[str]


@apps_router.put("/sync_installed_apps/android",
                 response_model=SyncInstalledAppsResponse)
def sync_installed_apps(
    current_user=CurrentUserDependecy(),
    session=SessionDependecy(),
    apps: list[mapp.AppSchemeCreateAndroid] = fastapi.Body(
        embed=True),
):
    send_icons: list[mapp.App] = []
    determined_apps: list[mapp.App] = []
    for app_data in apps:
        is_new, app = mapp.determine_app_android(session, app_data)
        determined_apps.append(app)
        if app.is_visible():
            if is_new:
                send_icons.append(app)
            elif app.approved and app.icon_preview is None:
                send_icons.append(app)
    mapp.set_apps_to_user(session, current_user, determined_apps)

    session.commit()

    return {
        "apps": mapp.get_user_apps(session,
                                   current_user, only_visible=True),
        # deprecated
        "send_icons_apps_ids": list(map(lambda app: app.id, send_icons)),
        "send_icons_apps_android_packages": list(map(
            lambda app: app.android_package_name, send_icons)),
    }


@apps_router.get("/app/{app_id}", response_model=AppScheme)
def get_app_by_id(
    app_id,
    session: sqlalchemy.orm.Session = SessionDependecy()
):
    app = mapp.get_app(session, id=app_id)
    if not app:
        raise fastapi.HTTPException(404)
    return app


class SetIconsRequestBody(pydantic.BaseModel):
    icon_preview: pydantic.FileUrl | None = None


@apps_router.put("/app/package/{package_name}/set_images",
                 response_model=AppScheme)
@apps_router.put("/app/package/{package_name}/set_icon",
                 response_model=AppScheme)
async def set_images(
    package_name,
    icon: fastapi.UploadFile = fastapi.File(),
    session: sqlalchemy.orm.Session = SessionDependecy(),
):
    app = mapp.get_app(session, android_package_name=package_name)
    if app is None:
        raise fastapi.HTTPException(
            400,
            detail="bad app"
        )
    if app.icon_preview:
        raise fastapi.HTTPException(
            400,
            detail="already set"
        )
    app.icon_preview = nux.s3.upload_fastapi_file(
        icon,
        "icons", "icon_preview", package_name
    )
    session.commit()
    session.merge(app)
    return app


class GetUserAppsResponse(pydantic.BaseModel):
    apps: list[AppScheme]


# deprecated
@apps_router.get("/user/{user_id}/apps", response_model=GetUserAppsResponse)
def get_user_apps(
    user_id: str,
    session: sqlalchemy.orm.Session = SessionDependecy(),
):
    user = muser.get_user(session, user_id)
    if user is None:
        raise fastapi.HTTPException(
            404,
            detail="bad user"
        )
    return {
        "apps": mapp.get_user_apps(session, user, only_visible=True)
    }


class GetUserAppsResponseV2(pydantic.BaseModel):
    apps_and_stats: list[AppAndUserStatisticsScheme]


@apps_router.get("/apps/friend/{user_id}/v2",
                 response_model=GetUserAppsResponseV2)
def get_friend_apps_v2(
    user_id: str,
    session: sqlalchemy.orm.Session = SessionDependecy(),
):
    user = muser.get_user(session, user_id)
    if user is None:
        raise fastapi.HTTPException(
            404,
            detail="bad user"
        )
    return {
        "apps_and_stats": mapp.get_user_apps_and_stats(
            session, user, only_visible=True)
    }


@apps_router.get("/apps/current_user/v2", response_model=GetUserAppsResponseV2)
def get_current_user_apps_v2(
    current_user: muser.User = CurrentUserDependecy(),
    session: sqlalchemy.orm.Session = SessionDependecy(),
):
    return {
        "apps_and_stats": mapp.get_user_apps_and_stats(
            session, current_user, only_visible=True),
    }


class RecomendationsAppsResponse(pydantic.BaseModel):
    apps: list[AppScheme]


@apps_router.get("/apps/recommendations",
                 response_model=RecomendationsAppsResponse)
def get_recommended_apps(
    current_user=CurrentUserDependecy(),
    session: sqlalchemy.orm.Session = SessionDependecy(),
):
    return {
        "apps": mapp.get_recommended_apps(session, current_user),
    }


class LocalUserInAppRecordScheme(pydantic.BaseModel):
    android_package_name: str
    dt_begin: datetime.datetime
    dt_end: datetime.datetime


@apps_router.put("/apps/statistics/update_from_local/android")
def statistics_update_from_local(
        local_records: list[LocalUserInAppRecordScheme] =
        fastapi.Body(embed=True),
        current_user: muser.User = CurrentUserDependecy(),
        session: sqlalchemy.orm.Session = SessionDependecy(),
):
    for local_record in local_records:
        app = mapp.get_app(
            session,
            android_package_name=local_record.android_package_name
        )
        mapp.add_user_in_app_record(
            session,
            current_user,
            app,
            local_record.dt_begin,
            local_record.dt_end
        )
    mapp.update_periodic_stats(session, current_user)
    session.commit()
