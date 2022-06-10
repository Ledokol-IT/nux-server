import datetime
import fastapi
import fastapi.params
import fastapi.security
import pydantic
import jose.jwt

from nux.database import SessionDependecy
from nux.config import options

auth_router = fastapi.APIRouter()

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jose.jwt.encode(to_encode, options.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: fastapi.security.OAuth2PasswordRequestForm = fastapi.params.Depends()):  # type: ignore
    # user = authenticate_user(
    #     fake_users_db, form_data.username, form_data.password)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    access_token_expires = datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "123"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

