import fastapi
import pydantic
import sqlalchemy.orm

from nux.auth import CurrentUserDependecy
from nux.database import SessionDependecy
import nux.notifications
import nux.models.user
import nux.models.app
import nux.s3

from typing import Union


user_router = fastapi.APIRouter()


@user_router.get("/get_me",
                 response_model=nux.models.user.UserScheme)
def get_me(user=CurrentUserDependecy()):
    """Get authenticated user"""
    return user


@user_router.get("/users/",
                 response_model=nux.models.user.UserSchemeSecure)
def get_user_by_parameter(
        phone: Union[str, None] = None,
        nickname: Union[str, None] = None,
        session=SessionDependecy()
):
    """Accept only one parameter"""
    user = None
    if phone and nickname:
        raise fastapi.HTTPException(400)
    elif phone:
        user = nux.models.user.get_user(session, phone=phone)
    elif nickname:
        user = nux.models.user.get_user(session, nickname=nickname)

    if not user:
        raise fastapi.HTTPException(404)
    return user


class CheckExistingUserResponseScheme(pydantic.BaseModel):
    exists: bool


@user_router.get("/users/check/",
                 response_model=CheckExistingUserResponseScheme)
def check_existing_user(
        phone: Union[str, None] = None,
        nickname: Union[str, None] = None,
        session=SessionDependecy()
):
    """Accepts only one parameter"""
    user = None
    if phone and nickname:
        raise fastapi.HTTPException(400)
    elif phone:
        user = nux.models.user.get_user(session, phone=phone)
    elif nickname:
        user = nux.models.user.get_user(session, nickname=nickname)

    return {"exists": user is not None}


@user_router.get("/user/{user_id}",
                 response_model=nux.models.user.UserSchemeSecure)
def get_user_by_id(user_id: str, session=SessionDependecy()):
    user = nux.models.user.get_user(session, id=user_id)
    if not user:
        raise fastapi.HTTPException(404)
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
        nux.models.user.get_user(session, friend_id)
        for friend_id in body.friends_ids
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


class SetDoNotDisturbRequestBody(pydantic.BaseModel):
    do_not_disturb: bool


@user_router.put("/current_user/do_not_disturb",
                 response_model=nux.models.user.UserScheme)
def set_do_not_disturb(
    body: SetDoNotDisturbRequestBody,
    session=SessionDependecy(),
    current_user: "nux.models.user.User" = CurrentUserDependecy(),
):
    current_user.do_not_disturb = body.do_not_disturb
    session.commit()
    return current_user


class SetProfilePicRequestBody(pydantic.BaseModel):
    profile_pic: pydantic.FileUrl


@user_router.put("/user/{user_id}/profile_pic",
                 response_model=nux.models.user.UserScheme)
def set_profile_pic_admin(
    user_id,
    body: SetProfilePicRequestBody,
    session: sqlalchemy.orm.Session = SessionDependecy()
):
    user = nux.models.user.get_user(session, user_id)
    if user is None:
        raise fastapi.HTTPException(
            404,
            detail="bad user"
        )
    user.profile_pic = body.profile_pic
    session.merge(user)
    session.commit()
    return user


@user_router.put("/current_user/profile_pic",
                 response_model=nux.models.user.UserScheme)
def set_profile_pic(
    session: sqlalchemy.orm.Session = SessionDependecy(),
    current_user: 'nux.models.user.User' = CurrentUserDependecy(),
    profile_pic: fastapi.UploadFile = fastapi.File(),
):
    url = nux.s3.upload_fastapi_file(profile_pic, 'users', 'profile_pic', None)
    current_user.profile_pic = url
    session.commit()
    return current_user
