import datetime
import fastapi
import fastapi.params
import fastapi.security
import pydantic
import jose.jwt
from sqlalchemy.orm.session import Session

from nux.database import SessionDependecy
import nux.config as config
import nux.confirmation
import nux.models.user
import nux.pydantic_types
from nux.models.user import User, get_user, create_user, UserSchemeCreate

auth_router = fastapi.APIRouter()

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
ALGORITHM = "HS256"


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


def create_token(user: User, expires_delta: datetime.timedelta | None = None):
    user_id = str(user.id)

    if expires_delta is None:
        expires_delta = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.datetime.utcnow() + expires_delta

    access_token = {"exp": expire, "sub": user_id}
    access_token = jose.jwt.encode(
        access_token, config.SECRET_KEY, algorithm=ALGORITHM)

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


def authenticate_user(
    session: Session,
    username: str,
    password: str,
) -> User | None:
    if username.startswith("+"):
        user = get_user(session, phone=username)
    else:
        user = get_user(session, nickname=username)

    if user is None:
        return None
    if not user.check_password(password):
        return None

    return user


@auth_router.post("/token", response_model=Token)
def login_with_password(
    form_data: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
    session=SessionDependecy(),
):
    user = authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token(user)


@auth_router.post("/login", response_model=Token)
def login_with_phone_confirmation(
    phone_confirmation: nux.confirmation.PhoneConfirmationRequestScheme,
    phone: nux.pydantic_types.Phone = fastapi.Body(),
    session=SessionDependecy(),
):
    if not nux.confirmation.check_phone_confirmation(
        session,
        id=phone_confirmation.id,
        phone=phone,
        code=phone_confirmation.code,
        reason='login',
    ):
        raise fastapi.HTTPException(401, "Bad phone confirmation")
    user = nux.models.user.get_user(session, phone=phone)
    if not user:
        raise fastapi.HTTPException(
            status_code=401,
            detail="Phone not registered",
        )
    return create_token(user)


class RegistrationUserDataRequestScheme(UserSchemeCreate):
    phone: nux.pydantic_types.Phone


@auth_router.post("/register", response_model=Token)
def register(
        user: RegistrationUserDataRequestScheme,
        phone_confirmation: nux.confirmation.PhoneConfirmationRequestScheme,
        session=SessionDependecy()
):
    if not nux.confirmation.check_phone_confirmation(
        session,
        id=phone_confirmation.id,
        phone=user.phone,
        code=phone_confirmation.code,
        reason='registration',
    ):
        raise fastapi.HTTPException(401, "Bad phone confirmation")
    user = create_user(user)
    if user is None:
        raise fastapi.HTTPException(
            status_code=500,
            detail="Cannot create user",
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return create_token(user)


def get_current_user(
    token: str = fastapi.Depends(oauth2_scheme),
    session=SessionDependecy()
) -> User:
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jose.jwt.decode(
            token, config.SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        if id is None:
            raise credentials_exception
    except jose.jwt.JWTError:
        raise credentials_exception
    user = get_user(session, id=id)
    if user is None:
        raise credentials_exception
    return user


def CurrentUserDependecy():
    """Actualy it's fake type and it
    returns fastapi.Depends(get_current_user)
    """
    return fastapi.Depends(get_current_user, use_cache=True)
