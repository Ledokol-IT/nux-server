import typing as t
import uuid

import passlib.context
import pydantic
import sqlalchemy as sa
import sqlalchemy.orm as orm

import nux.database
import nux.models.app
import nux.models.status


pwd_context = passlib.context.CryptContext(
    schemes=["bcrypt"], deprecated="auto")


class User(nux.database.Base):
    __tablename__ = "users"

    id: str = sa.Column(
        sa.String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )  # type: ignore
    # In +79999999999 format
    phone: str = sa.Column(
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
    hashed_password: str = sa.Column(sa.String, nullable=False)  # type: ignore
    firebase_messaging_token: str = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    profile_pic: str = sa.Column(
        sa.String,
        nullable=True
    )  # type: ignore
    DEFAULT_PROFILE_PIC = "https://storage.yandexcloud.net/nux/icons/common/profile_pic_base.png"

    status: 'nux.models.status.UserStatus' = orm.relationship(
        lambda: nux.models.status.UserStatus,
        uselist=False,
        back_populates="_user",
    )

    apps_stats: 'nux.models.app.UserInAppStatistic' = orm.relationship(
        lambda: nux.models.app.UserInAppStatistic,
        back_populates="user"
    )

    do_not_disturbe_mode: bool = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
    )  # type: ignore

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)


class UserSchemeBase(pydantic.BaseModel):
    nickname: str
    name: str


class UserSchemeCreate(UserSchemeBase):
    password: str


class UserSchemeSecure(UserSchemeBase):
    id: str
    status: t.Optional['nux.models.status.UserStatusSchemeSecure']
    profile_pic: str
    do_not_disturbe_mode: bool

    @pydantic.validator('profile_pic', pre=True)
    def set_default_profile_pic(cls, v):
        return v or User.DEFAULT_PROFILE_PIC
        

    class Config:
        orm_mode = True


class UserScheme(UserSchemeSecure):
    phone: str | None
    status: t.Optional['nux.models.status.UserStatusScheme']

    class Config:
        orm_mode = True


def create_user(user_data: UserSchemeCreate):
    user = User()
    user.nickname = user_data.nickname
    user.name = user_data.name
    user.set_password(user_data.password)
    user.status = nux.models.status.create_empty_status()
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


def get_friends(
    session: orm.Session,
    user: User,
    order: t.Literal["online"] | None = None,
) -> list[User]:
    query = (
        session.query(User)
        .join(User.status)
        .filter(User.id != user.id)
    )
    if order == "online":
        query = query.order_by(nux.models.status.UserStatus.dt_last_update)

    friends = query.all()

    return friends
