import fastapi

from nux.auth import CurrentUserDependecy
from nux.models.user import UserScheme


user_router = fastapi.APIRouter()


@user_router.get("/get_me", response_model=UserScheme)
def get_me(user=CurrentUserDependecy()):
    return user
