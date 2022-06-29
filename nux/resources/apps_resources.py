import fastapi
import pydantic

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
