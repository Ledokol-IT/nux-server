import fastapi
import pydantic
import sqlalchemy.orm

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
import nux.models.user
import nux.models.app


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
    determined_apps: list[nux.models.app.App] = [
        nux.models.app.determine_app_android(session, app_data)[1]
        for app_data in apps
    ]
    nux.models.app.set_apps_to_user(session, current_user, determined_apps)

    session.commit()

    return {
        "apps": nux.models.app.get_user_apps(session, current_user)
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
    body: SetIconsRequestBody,
    session: sqlalchemy.orm.Session = SessionDependecy()
):
    app = nux.models.app.get_app(session, android_package_name=package_name)
    if app is None:
        raise fastapi.HTTPException(
            400,
            detail="bad app"
        )
    if body.icon_preview:
        app.icon_preview = body.icon_preview
    if body.icon_large:
        app.icon_large = body.icon_large
    if body.image_wide:
        app.image_wide = body.image_wide
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
