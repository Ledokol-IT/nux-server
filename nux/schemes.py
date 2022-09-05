from __future__ import annotations
import typing as t
import pydantic
import datetime
import nux.pydantic_types
import nux.default_profile_pics

CATEGORY = t.Literal["GAME", "GAME,online", "OTHER"]


class UserSchemeEdit(pydantic.BaseModel):
    nickname: str | None = None
    name: str | None = None
    default_profile_pic_id: str | None = None

    @pydantic.validator("default_profile_pic_id")
    def check_default_profile_pic_id(cls, v):
        if v is None:
            return None
        if v not in nux.default_profile_pics.profile_pics_ids:
            raise ValueError("This profile pic id does not exist")
        return v


class UserSchemeCreate(UserSchemeEdit):
    nickname: str
    name: str
    password: str | None = None
    phone: nux.pydantic_types.Phone | None = None


class UserN(pydantic.BaseModel):
    _DEFAULT_PROFILE_PIC = "https://storage.yandexcloud.net/nux/icons/common/profile_pic_base.png"  # noqa
    id: str
    nickname: str
    name: str
    profile_pic: str

    @pydantic.validator('profile_pic', pre=True)
    def set_default_profile_pic(cls, v):
        return v or cls._DEFAULT_PROFILE_PIC

    class Config:
        orm_mode = True


class UserSchemeSecure(UserN):
    status: t.Optional[UserStatusSchemeSecure]
    profile_pic: str
    do_not_disturb: bool

    class Config:
        orm_mode = True


class UserScheme(UserSchemeSecure):
    phone: str | None
    status: t.Optional[UserStatusScheme]

    class Config:
        orm_mode = True


class UserStatusSchemeSecure(pydantic.BaseModel):
    id: str
    app: t.Optional[AppScheme]
    dt_last_update: datetime.datetime
    dt_entered_app: datetime.datetime | None
    dt_leaved_app: datetime.datetime | None
    in_app: bool
    online: bool

    class Config:
        orm_mode = True


class UserStatusScheme(UserStatusSchemeSecure):
    pass


class AppSchemeBase(pydantic.BaseModel):
    android_package_name: str | None
    name: str


class AppSchemeCreateAndroid(AppSchemeBase):
    android_package_name: str
    android_category: int | None


class AppN(pydantic.BaseModel):
    _DEFAULT_ICON_PREVIEW = "https://storage.yandexcloud.net/nux/icons/common/preview_icon.png"  # noqa
    id: str
    name: str
    android_package_name: str
    icon_preview: str

    @pydantic.validator("icon_preview", pre=True, check_fields=False)
    def set_default_app_icon_preview(cls, value):
        return value or cls._DEFAULT_ICON_PREVIEW

    class Config:
        orm_mode = True


class AppScheme(AppN):
    category: CATEGORY

    class Config:
        orm_mode = True


class PendingFriendsInviteScheme(pydantic.BaseModel):
    dt_sent: datetime.datetime
    from_user: UserSchemeSecure

    class Config:
        orm_mode = True


class OutgoingFriendsInviteScheme(pydantic.BaseModel):
    dt_sent: datetime.datetime
    to_user: UserSchemeSecure

    class Config:
        orm_mode = True


UserSchemeEdit.update_forward_refs()
UserSchemeCreate.update_forward_refs()
UserSchemeSecure.update_forward_refs()
UserScheme.update_forward_refs()

UserStatusSchemeSecure.update_forward_refs()
UserStatusScheme.update_forward_refs()

AppSchemeCreateAndroid.update_forward_refs()
AppScheme.update_forward_refs()

PendingFriendsInviteScheme.update_forward_refs()
OutgoingFriendsInviteScheme.update_forward_refs()
