import sqlalchemy as sa
import nux.database

class User(nux.database.Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    phone = sa.Column(sa.String, index=True, unique=True) # In +79999999999 format
    nickname = sa.Column(sa.String, index=True)
    hashed_password = sa.Column(sa.String)

    def _hash_password(password: str) -> str:
        pass
