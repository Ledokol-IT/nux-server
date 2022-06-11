import pydantic
import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.dialects.postgresql
import passlib.context

import uuid

import nux.database


pwd_context = passlib.context.CryptContext(
    schemes=["bcrypt"], deprecated="auto")


class User(nux.database.Base):
    __tablename__ = "users"

    id: uuid.UUID = sa.Column(sqlalchemy.dialects.postgresql.UUID,
                              primary_key=True, index=True, default=uuid.uuid4)  # type: ignore
    # In +79999999999 format
    phone = sa.Column(sa.String, index=True, unique=True,
                      nullable=True)  # type: ignore
    nickname: str = sa.Column(sa.String, index=True,
                              nullable=False)  # type: ignore
    hashed_password: str = sa.Column(sa.String, nullable=False)  # type: ignore

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

    class Config:
        org_mode = True


class UserScheme(UserSchemeSecure):
    phone: str

    class Config:
        org_mode = True


def create_user(user_data: UserSchemeCreate):
    user = User()
    user.nickname = user_data.nickname
    user.set_password(user_data.password)
    return user


def get_user(session: sqlalchemy.orm.Session, id: uuid.UUID | str | None = None, phone: str | None = None, nickname: str | None = None):
    cnt_args = sum(map(lambda x: x is not None, [id, phone, nickname]))
    if cnt_args != 1:
        raise ValueError(f"Expected 1 argument. Find {cnt_args}")

    query = session.query(User)
    user = None
    if id is not None:
        if isinstance(id, str):
            id = uuid.UUID(id)
        user = query.get(id)
    elif phone is not None:
        user = query.filter(User.phone == phone).first()
    elif nickname is not None:
        user = query.filter(User.nickname == nickname).first()
    
    return user
