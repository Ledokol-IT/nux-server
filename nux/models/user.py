from __future__ import annotations
import typing as t
import uuid

import passlib.context
import pydantic
import sqlalchemy as sa
import sqlalchemy.orm as orm

import nux.database
import nux.default_profile_pics
import nux.pydantic_types


pwd_context = passlib.context.CryptContext(
    schemes=["bcrypt"], deprecated="auto")


class User(nux.database.Base):
    __tablename__ = "users"

    id: str = sa.Column(
        sa.String,
        primary_key=True,
    )  # type: ignore

    @staticmethod
    def _generate_id():
        return str(uuid.uuid4())

    # In +79999999999 format
    phone: str | None = sa.Column(
        sa.String,
        index=True,
        unique=True,
        nullable=True,
    )  # type: ignore
    nickname: str = sa.Column(sa.String, index=True, unique=True,
                              nullable=False)  # type: ignore
    name: str = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    hashed_password: str | None = sa.Column(
        sa.String, nullable=True)  # type: ignore
    firebase_messaging_token: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore

    do_not_disturb: bool = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
    )  # type: ignore

    profile_pic: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    _default_profile_pic_id: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    DEFAULT_PROFILE_PIC = \
        "https://storage.yandexcloud.net/nux/icons/common/profile_pic_base.png"

    status: mstatus.UserStatus | None = orm.relationship(
        lambda: mstatus.UserStatus,
        uselist=False,
        back_populates="_user",
    )
    apps_stats: list[mapp.UserInAppStatistic] = orm.relationship(
        lambda: mapp.UserInAppStatistic,
        cascade="all,delete",
        back_populates="user",
    )

    pending_friends_invites: list[mfriends.FriendsInvite]
    pending_friends_invites = orm.relationship(
        lambda: mfriends.FriendsInvite,
        cascade="all,delete",
        back_populates="to_user",
        foreign_keys=lambda: [mfriends.FriendsInvite.to_user_id],
    )
    outgoing_friends_invites: list[mfriends.FriendsInvite]
    outgoing_friends_invites = orm.relationship(
        lambda: mfriends.FriendsInvite,
        cascade="all,delete",
        back_populates="from_user",
        foreign_keys=lambda: [mfriends.FriendsInvite.from_user_id],
    )

    _friendships1: list[mfriends.Friendship] = orm.relationship(
        lambda: mfriends.Friendship,
        cascade="all,delete",
        back_populates="user1",
        foreign_keys=lambda: [mfriends.Friendship.user1_id],
    )
    _friendships2: list[mfriends.Friendship] = orm.relationship(
        lambda: mfriends.Friendship,
        cascade="all,delete",
        back_populates="user2",
        foreign_keys=lambda: [mfriends.Friendship.user2_id],
    )

    def check_password(self, password: str) -> bool:
        if self.hashed_password is None:
            return False
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)


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


class UserSchemeSecure(pydantic.BaseModel):
    id: str
    nickname: str
    name: str
    status: t.Optional['mstatus.UserStatusSchemeSecure']
    profile_pic: str
    do_not_disturb: bool

    @pydantic.validator('profile_pic', pre=True)
    def set_default_profile_pic(cls, v):
        return v or User.DEFAULT_PROFILE_PIC

    class Config:
        orm_mode = True


class UserScheme(UserSchemeSecure):
    phone: str | None
    status: t.Optional['mstatus.UserStatusScheme']

    class Config:
        orm_mode = True


def create_user(user_data: UserSchemeCreate):
    user = User()
    user.id = User._generate_id()
    user.nickname = user_data.nickname
    user.name = user_data.name
    if user_data.password is not None:
        user.set_password(user_data.password)
    user.status = mstatus.create_empty_status()
    user.phone = user_data.phone

    user._default_profile_pic_id = (
        user_data.default_profile_pic_id
        or nux.default_profile_pics.get_random_id()
    )
    user.profile_pic = nux.default_profile_pics.get_url_by_id(
        user._default_profile_pic_id
    )

    return user


def edit_user(
        session: orm.Session,
        user: User,
        user_data: UserSchemeEdit
):
    _ = session
    if user_data.nickname is not None:
        user.nickname = user_data.nickname
    if user_data.name is not None:
        user.name = user_data.name

    if user_data.default_profile_pic_id is not None:
        user._default_profile_pic_id = user_data.default_profile_pic_id
        user.profile_pic = nux.default_profile_pics.get_url_by_id(
            user._default_profile_pic_id
        )
    return user


def get_user(
    session: orm.Session,
    id: str | None = None,
    phone: str | None = None,
    nickname: str | None = None
) -> User | None:
    cnt_args = sum(map(lambda x: x is not None, [id, phone, nickname]))
    if cnt_args != 1:
        raise ValueError(f"Expected 1 argument. Find {cnt_args}")

    query = session.query(User)
    user = None
    if id is not None:
        user = query.get(id)
    elif phone is not None:
        user = query.filter(User.phone == phone).first()
    elif nickname is not None:
        user = query.filter(User.nickname == nickname).first()

    return user


import nux.models.app as mapp
import nux.models.status as mstatus
import nux.models.friends as mfriends
UserSchemeEdit.update_forward_refs()
UserSchemeCreate.update_forward_refs()
UserSchemeSecure.update_forward_refs()
UserScheme.update_forward_refs()
