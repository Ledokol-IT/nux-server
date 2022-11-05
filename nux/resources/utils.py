import fastapi

import nux.models.user as muser
from nux.database import SessionDependecy


def get_user_or_raise(
        user_id_field: str,
        code=404,
        detail=None,
) -> muser.User:
    if detail is None:
        detail = f"Error in {user_id_field}: not found."

    def _validate(
            session=SessionDependecy(),
            user_id=fastapi.Query(alias=user_id_field),
    ):
        user = muser.get_user(session, id=user_id)
        if not user:
            raise fastapi.HTTPException(code, detail)
        return user

    return fastapi.Depends(_validate)
