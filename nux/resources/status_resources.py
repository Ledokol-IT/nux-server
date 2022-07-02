import fastapi

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
from nux.models.status import UserStatusScheme, update_status_in_app, update_status_leave_app
from nux.models.app import AppSchemeCreateAndroid, determine_app_android

status_router = fastapi.APIRouter()


@status_router.put("/status/set/android", response_model=UserStatusScheme)
def set_status(
        app: AppSchemeCreateAndroid = fastapi.Body(embed=True),
        current_user=CurrentUserDependecy(),
        session=SessionDependecy(),
):
    _, app = determine_app_android(session, app)
    status = update_status_in_app(session, current_user, app)

    session.commit()
    session.refresh(status)
    return status


@status_router.put("/status/leave", response_model=UserStatusScheme)
def unset_status(
        current_user=CurrentUserDependecy(),
        session=SessionDependecy(),
):
    status = update_status_leave_app(session, current_user)
    session.commit()
    if session is not None:
        session.refresh(status)
    return status
