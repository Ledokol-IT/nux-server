import fastapi
import pydantic

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
from nux.models.app import AppSchemeCreateAndroid
import nux.notifications
import nux.models.user
import nux.models.app

user_router = fastapi.APIRouter()


@user_router.get("/get_me",
                 response_model=nux.models.user.UserScheme)
def get_me(user=CurrentUserDependecy()):
    """Get authenticated user"""
    return user


@user_router.get("/user/{user_id}",
                 response_model=nux.models.user.UserSchemeSecure)
def get_user_by_nickname(user_id: str, session=SessionDependecy()):
    user = nux.models.user.get_user(session, id=user_id)
    return user


@user_router.get("/friends",
                 response_model=list[nux.models.user.UserSchemeSecure])
def get_friends_request(
    current_user=CurrentUserDependecy(),
    session=SessionDependecy()
):
    friends = nux.models.user.get_friends(session, current_user, "online")
    return friends


class InviteFriendsRequestBody(pydantic.BaseModel):
    friends_ids: list[str]
    app_id: str


@user_router.post("/friends/invite")
def invite_friends_to_game(
    body: InviteFriendsRequestBody,
    background_tasks: fastapi.BackgroundTasks,
    session=SessionDependecy(),
    current_user: 'nux.models.user.User' = CurrentUserDependecy(),
):
    not_validated_friends = (
        nux.models.user.get_user(session, friend_id) for friend_id in body.friends_ids
    )
    friends = []
    for friend in not_validated_friends:
        if friend is None:
            raise fastapi.HTTPException(
                status_code=404,
                detail="bad friend_id",
            )
        else:
            friends.append(friend)
    app = nux.models.app.get_app(session, body.app_id)
    if not app:
        raise fastapi.HTTPException(
            status_code=404,
            detail="bad app_id",
        )
    print(friends)
    background_tasks.add_task(
        nux.notifications.send_invite_to_app_from_friend,
        session,
        current_user,
        friends,
        app,
    )


class SetMessagingTokenRequestBody(pydantic.BaseModel):
    firebase_messaging_token: str


@user_router.put("/current_user/firebase_messaging_token")
def set_messaging_token(
    body: SetMessagingTokenRequestBody,
    session=SessionDependecy(),
    current_user: "nux.models.user.User" = CurrentUserDependecy(),
):
    current_user.firebase_messaging_token = body.firebase_messaging_token
    session.commit()
