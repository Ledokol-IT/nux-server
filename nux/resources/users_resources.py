import fastapi

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
from nux.models.user import UserScheme, UserSchemeSecure, get_user


user_router = fastapi.APIRouter()


@user_router.get("/get_me", response_model=UserScheme)
def get_me(user=CurrentUserDependecy()):
    """Get authenticated user"""
    return user


@user_router.get("/user/{nickname}", response_model=UserSchemeSecure)
def get_user_by_nickname(nickname: str, session=SessionDependecy()):
    user = get_user(session, nickname=nickname)
    return user


@user_router.get("/friends", response_model=list[UserSchemeSecure])
def get_friends(current_user=CurrentUserDependecy(), session=SessionDependecy()):
    """get friends in last_actvivty order"""
    # TODO: implement
    pass
