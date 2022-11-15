from http import HTTPStatus

import fastapi
import pydantic

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
from nux.events import EventsDependecy
import nux.models.app as mapp
import nux.models.friends as mfriends
import nux.models.user as muser
import nux.notifications
import nux.s3
from nux.schemes import UserSchemeSecure
from nux.resources.utils import UserQueryParam


router = fastapi.APIRouter(prefix="/statistic")


@router.get("/friend/{user_id}",
            response_model=None)
def get_friend_statistic(
        current_user=CurrentUserDependecy(),
        session=SessionDependecy()
):
    friends = mfriends.get_friends(session, current_user, "online")
    return friends


@router.put("/add")
def add_friend(
        user_id: str = fastapi.Body(embed=True),
        current_user=CurrentUserDependecy(),
        session=SessionDependecy(),
        events=EventsDependecy(),
):
    """Both for sending and accepting invites"""
    to_user = muser.get_user(session, id=user_id)
    if to_user is None:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="bad user_id",
        )
    if to_user == current_user:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="can't send request to yourself",
        )

    mfriends.add_user_as_friend(session, events, current_user, to_user)
    session.commit()
