import pydantic
import typing as t
import sqlalchemy as sa
import sqlalchemy.orm as orm
import passlib.context

import uuid

import nux.database
import nux.models.status
import nux.models.app


pwd_context = passlib.context.CryptContext(
    schemes=["bcrypt"], deprecated="auto")


class User(nux.database.Base):
    __tablename__ = "users"

    id: str = sa.Column(sa.String,
                        primary_key=True, index=True, default=lambda: str(uuid.uuid4()))  # type: ignore
    # In +79999999999 format
    phone = sa.Column(sa.String, index=True, unique=True,
                      nullable=True)  # type: ignore
    nickname: str = sa.Column(sa.String, index=True,
                              nullable=False)  # type: ignore
    hashed_password: str = sa.Column(sa.String, nullable=False)  # type: ignore

    status: t.Optional['nux.models.status.UserStatus'] = orm.relationship(
        lambda: nux.models.status.UserStatus, uselist=False, back_populates="_user")

    apps = orm.relationship(
        lambda: nux.models.app.App,
        primaryjoin=lambda: nux.models.app.UserInAppStatistic.user_id == id,
    )
    apps_stats: 'nux.models.app.UserInAppStatistic' = orm.relationship(
        lambda: nux.models.app.UserInAppStatistic,
        back_populates="_user"
    )

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)


class UserSchemeBase(pydantic.BaseModel):
    nickname: str


class UserSchemeCreate(UserSchemeBase):
    password: str


class UserSchemeSecure(UserSchemeBase):
    id: str
    status: t.Optional['nux.models.status.UserStatusSchemeSecure']

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
    user.set_password(user_data.password)
    return user


def get_user(session: orm.Session, id: str | None = None, phone: str | None = None, nickname: str | None = None):
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


def get_friends(session: orm.Session, user: User, order="online") -> list[User]:
    friends = (
        session.query(User)
        .join(User.status)
        .order_by(nux.models.status.UserStatus.last_update)
    ).all()

    return friends
