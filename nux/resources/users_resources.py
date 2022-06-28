import fastapi

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
import nux.models.user


user_router = fastapi.APIRouter()


@user_router.get("/get_me",
                 response_model=nux.models.user.UserScheme)
def get_me(user=CurrentUserDependecy()):
    """Get authenticated user"""
    return user


@user_router.get("/user/{nickname}",
                 response_model=nux.models.user.UserSchemeSecure)
def get_user_by_nickname(nickname: str, session=SessionDependecy()):
    user = nux.models.user.get_user(session, nickname=nickname)
    return user


@user_router.get("/friends",
                 response_model=list[nux.models.user.UserSchemeSecure])
def get_friends_request(current_user=CurrentUserDependecy(), session=SessionDependecy()):
    friends = nux.models.user.get_friends(session, current_user)
    return friends
