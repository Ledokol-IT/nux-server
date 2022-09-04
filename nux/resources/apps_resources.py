from __future__ import annotations

import fastapi
import pydantic
import sqlalchemy.orm

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
import nux.models.app
import nux.models.user
import nux.s3


apps_router = fastapi.APIRouter()


class SyncInstalledAppsResponse(pydantic.BaseModel):
    apps: list[nux.models.app.AppScheme]


@apps_router.put("/sync_installed_apps/android",
                 response_model=SyncInstalledAppsResponse)
def sync_installed_apps(
    current_user=CurrentUserDependecy(),
    session=SessionDependecy(),
    apps: list[nux.models.app.AppSchemeCreateAndroid] = fastapi.Body(
        embed=True),
):
    send_icons = []
    determined_apps: list[nux.models.app.App] = []
    for app_data in apps:
        is_new, app = nux.models.app.determine_app_android(session, app_data)
        determined_apps.append(app)
        if is_new:
            send_icons.append(app.id)
    nux.models.app.set_apps_to_user(session, current_user, determined_apps)

    session.commit()

    return {
        "apps": nux.models.app.get_user_apps(session, current_user),
        "send_icons_apps_ids": send_icons,
    }


@apps_router.get("/app/{app_id}", response_model=nux.models.app.AppScheme)
def get_app_by_id(
    app_id,
    session: sqlalchemy.orm.Session = SessionDependecy()
):
    app = nux.models.app.get_app(session, id=app_id)
    if not app:
        raise fastapi.HTTPException(404)
    return app


class SetIconsRequestBody(pydantic.BaseModel):
    icon_large: pydantic.FileUrl | None = None
    icon_preview: pydantic.FileUrl | None = None
    image_wide: pydantic.FileUrl | None = None


@apps_router.put("/app/package/{package_name}/set_images",
                 response_model=nux.models.app.AppScheme)
def set_images(
    package_name,
    icon_large: fastapi.UploadFile | None = fastapi.File(default=None),
    icon_preview: fastapi.UploadFile | None = fastapi.File(default=None),
    image_wide: fastapi.UploadFile | None = fastapi.File(default=None),
    current_user: nux.models.user.User = CurrentUserDependecy(),
    session: sqlalchemy.orm.Session = SessionDependecy(),
):
    app = nux.models.app.get_app(session, android_package_name=package_name)
    if app is None:
        raise fastapi.HTTPException(
            400,
            detail="bad app"
        )
    if icon_large is not None:
        app.icon_large = nux.s3.upload_fastapi_file(
            icon_large,
            "icons", "icon_large", package_name
        )
    if icon_preview is not None:
        app.icon_preview = nux.s3.upload_fastapi_file(
            icon_preview,
            "icons", "icon_preview", package_name
        )
    if image_wide is not None:
        app.image_wide = nux.s3.upload_fastapi_file(
            image_wide,
            "icons", "image_wide", package_name
        )
    session.commit()
    session.merge(app)
    return app


class GetUserAppsResponse(pydantic.BaseModel):
    apps: list[nux.models.app.AppScheme]


@apps_router.get("/user/{user_id}/apps", response_model=GetUserAppsResponse)
def get_user_apps(
    user_id: str,
    session: sqlalchemy.orm.Session = SessionDependecy(),
):
    user = nux.models.user.get_user(session, user_id)
    if user is None:
        raise fastapi.HTTPException(
            404,
            detail="bad user"
        )
    return {
        "apps": nux.models.app.get_user_apps(session, user)
    }
