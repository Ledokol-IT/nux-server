"""module to handle phone, email (not realized) confirmations

It simulates microservice so encapsulate database work
(but still use project-wide Base and Session)
Module should not use other models (if possible)
"""

import datetime
import enum
import logging
import random
from typing import Literal
import uuid

import fastapi
import pydantic
import sqlalchemy as sa
from sqlalchemy.orm import Session

import nux.database
import nux.sms

logger = logging.getLogger(__name__)


class PhoneConfirmation(nux.database.Base):
    __tablename__ = 'confirmations'
    id: str = sa.Column(
        sa.String,
        primary_key=True,
    )  # type: ignore
    phone: str = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    code: str = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    reason: str = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    dt_created: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore
    TTL = datetime.timedelta(minutes=10)

    @property
    def expiration_dt(self):
        return self.dt_created + self.TTL


def generate_code():
    n_symbols = 4
    return str(random.randrange(10 ** (n_symbols - 1), 10 ** n_symbols))


class PhoneConfirmationScheme(pydantic.BaseModel):
    id: str
    phone: str
    dt_created: datetime.datetime
    expiration_dt: datetime.datetime

    class Config:
        orm_mode = True


class PhoneConfirmationRequestScheme(pydantic.BaseModel):
    id: str
    code: str


def create_phone_confirmation(
        session: Session,
        phone: str,
        reason: str,
) -> PhoneConfirmation:
    code = generate_code()
    confirmation = PhoneConfirmation()
    confirmation.id = str(uuid.uuid4())
    confirmation.phone = phone
    confirmation.code = code
    confirmation.dt_created = datetime.datetime.now()
    confirmation.reason = reason

    nux.sms.send_confirmation_code(phone, code)
    session.add(confirmation)
    return confirmation


def check_phone_confirmation(
        session: Session,
        id: str,
        phone: str,
        code: str,
        reason: str,
) -> bool:
    confirmation = session.query(PhoneConfirmation).get(id)
    if confirmation is None:
        return False
    if (
        confirmation.reason != reason
        or confirmation.phone != phone
        or (
            confirmation.code != code
        )
        or confirmation.expiration_dt < datetime.datetime.now()
    ):
        return False
    return True


confirmation_router = fastapi.APIRouter()


class PhoneConfirmationRequestBody(pydantic.BaseModel):
    phone: str
    reason: Literal['registration', 'login']


@confirmation_router.post("/confirmation/phone",
                          response_model=PhoneConfirmationScheme)
def post_phone_confirmation(
        body: PhoneConfirmationRequestBody,
        session: Session = nux.database.SessionDependecy(),
):
    confirmaion = create_phone_confirmation(session, body.phone, body.reason)
    session.commit()
    return confirmaion
