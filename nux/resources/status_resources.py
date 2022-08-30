
import fastapi

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
from nux.events import EventsDependecy
import nux.models.app as mapp
import nux.models.status

status_router = fastapi.APIRouter()


@status_router.put("/status/in_app/android",
                   response_model=nux.models.status.UserStatusScheme)
def set_status(
    app: mapp.AppSchemeCreateAndroid = fastapi.Body(embed=True),
    current_user=CurrentUserDependecy(),
    session=SessionDependecy(),
    events=EventsDependecy(),
):
    _, app = mapp.determine_app_android(session, app)
    status = nux.models.status.update_status_in_app(
        session, current_user, app, events)

    session.commit()
    session.refresh(status)
    return status


@status_router.put("/status/not_in_app",
                   response_model=nux.models.status.UserStatusScheme)
def unset_status(
    current_user=CurrentUserDependecy(),
    session=SessionDependecy(),
):
    status = nux.models.status.update_status_not_in_app(session, current_user)
    session.commit()
    session.refresh(status)
    return status
