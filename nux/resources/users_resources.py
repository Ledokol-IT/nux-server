import fastapi
import pydantic

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
from nux.models.app import AppSchemeCreateAndroid
import nux.models.user


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


@user_router.post("/friend/{friend_id}/invite")
def invite_friend_to_game(
    friend_id: str,
    app_id: str,
    session=SessionDependecy(),
    current_user: 'nux.models.user.User' = CurrentUserDependecy(),
):
    pass


class SetMessagingTokenRequestBody(pydantic.BaseModel):
    firebase_messaging_token: str


@user_router.put("/current_user/firebase_messaging_token")
def set_messaging_token(
    body: SetMessagingTokenRequestBody,
    session=SessionDependecy(),
    current_user: "nux.models.user.User" = CurrentUserDependecy(),
):
    current_user.firebase_messaging_token = body.firebase_messaging_token
    print(current_user.nickname)
    print(current_user.firebase_messaging_token)
    session.commit()
