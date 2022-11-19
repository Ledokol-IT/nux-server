import fastapi
from sqlalchemy import orm

import nux.models.user as muser
from nux.database import SessionDependecy


def get_user_or_raise(
        session: orm.Session,
        user_id: str,
        code: int,
        detail: str | None = None,
):
    user = muser.get_user(session, id=user_id)
    if not user:
        raise fastapi.HTTPException(code, detail)
    return user


def UserQueryParam(
        alias: str,
        code: int = 404,
        detail: str | None = None,
) -> muser.User:
    if detail is None:
        detail = f"Error in {alias}: user not found."

    def _validate(
            session=SessionDependecy(),
            # user_id=fastapi.Query(alias=alias),
            user_id=fastapi.Path(alias=alias)
    ):
        user = muser.get_user(session, id=user_id)
        if not user:
            raise fastapi.HTTPException(code, detail)
        return user

    return fastapi.Depends(_validate)
