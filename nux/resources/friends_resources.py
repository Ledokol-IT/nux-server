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


router = fastapi.APIRouter(prefix="/friends")


@router.get("/",
            response_model=list[muser.UserSchemeSecure])
def get_friends(
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


@router.get("/pending_invites",
            response_model=list[mfriends.PendingFriendsInviteScheme])
def get_pending_invites(
        current_user=CurrentUserDependecy(),
        session=SessionDependecy()
):
    return mfriends.get_pending_friends_invites(session, current_user)


@router.get("/outgoing_invites",
            response_model=list[mfriends.OutgoingFriendsInviteScheme])
def get_outgoing_invites(
        current_user=CurrentUserDependecy(),
        session=SessionDependecy()
):
    return mfriends.get_outgoing_friends_invites(session, current_user)


class InviteFriendsRequestBody(pydantic.BaseModel):
    friends_ids: list[str]
    app_id: str


@router.post("/invite")
def invite_friends_to_game(
        body: InviteFriendsRequestBody,
        background_tasks: fastapi.BackgroundTasks,
        session=SessionDependecy(),
        current_user: 'muser.User' = CurrentUserDependecy(),
):
    not_validated_friends = (
        muser.get_user(session, friend_id)
        for friend_id in body.friends_ids
    )
    friends = []
    user_friends_ids = set(map(
        lambda u: u.id,
        mfriends.get_friends(session, current_user)
    ))
    for friend in not_validated_friends:
        if friend is None:
            raise fastapi.HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="bad friend_id",
            )
        elif friend.id not in user_friends_ids:
            raise fastapi.HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="not your friend",
            )
        else:
            friends.append(friend)
    app = mapp.get_app(session, body.app_id)
    if not app:
        raise fastapi.HTTPException(
            status_code=404,
            detail="bad app_id",
        )
    background_tasks.add_task(
        nux.notifications.send_invite_to_app_from_friend,
        session,
        current_user,
        friends,
        app,
    )
