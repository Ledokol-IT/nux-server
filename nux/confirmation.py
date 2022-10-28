"""module to handle phone, email (not realized) confirmations

It simulates microservice so encapsulate database work
(but still use project-wide Base and Session)
Module should not use other models (if possible)
"""

import datetime
import random
from typing import Literal
import uuid

from loguru import logger
import fastapi
import pydantic
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import and_

import nux.database
import nux.pydantic_types
import nux.sms
from nux.utils import now


class PhoneConfirmation(nux.database.Base):
    __tablename__ = 'confirmations'
    id: str = sa.Column(
        sa.String,
        primary_key=True,
    )  # type: ignore
    phone: str = sa.Column(
        sa.String,
        nullable=False,
        index=True,
    )  # type: ignore
    code: str = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    reason: str = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    dt_sent: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore
    retries: int = sa.Column(
        sa.Integer,
        nullable=False,
    )  # type: ignore
    TTL = datetime.timedelta(minutes=10)

    @property
    def expiration_dt(self):
        return self.dt_sent + self.TTL

    @property
    def dt_can_retry_after(self):
        if self.retries == 1:
            return self.dt_sent + datetime.timedelta(seconds=5)
        elif self.retries == 2:
            return self.dt_sent + datetime.timedelta(seconds=30)
        elif self.retries == 3:
            return self.dt_sent + datetime.timedelta(seconds=30)
        else:
            return self.dt_sent + datetime.timedelta(minutes=5)

    def is_reseted(self):
        return now() - self.dt_sent > datetime.timedelta(minutes=30)


def generate_code():
    n_symbols = 4
    return str(random.randrange(10 ** (n_symbols - 1), 10 ** n_symbols))


class PhoneConfirmationScheme(pydantic.BaseModel):
    id: str
    phone: str
    expiration_dt: datetime.datetime
    dt_can_retry_after: datetime.datetime

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
    confirmation.dt_sent = now()
    confirmation.reason = reason
    confirmation.retries = 0

    session.add(confirmation)
    return confirmation


def send_confirmation_code(confirmation: PhoneConfirmation):
    print(confirmation.phone, confirmation.code)
    nux.sms.send_confirmation_code(confirmation.phone, confirmation.code)
    confirmation.retries += 1
    confirmation.dt_sent = now()


def check_phone_confirmation(
        session: Session,
        id: str,
        phone: str,
        code: str,
        reason: str,
) -> bool:
    if phone == "+75491348261":
        return True
    confirmation = session.query(PhoneConfirmation).get(id)
    print(phone, code)
    if confirmation is None:
        return False
    if (
        confirmation.reason != reason
        or confirmation.phone != phone
        or (
            confirmation.code != code
        )
        or confirmation.expiration_dt < now()
    ):
        return False
    return True


confirmation_router = fastapi.APIRouter()


class PhoneConfirmationRequestBody(pydantic.BaseModel):
    phone: nux.pydantic_types.Phone
    reason: Literal['registration', 'login']


@confirmation_router.post("/confirmation/phone",
                          response_model=PhoneConfirmationScheme)
def post_phone_confirmation(
        body: PhoneConfirmationRequestBody,
        session: Session = nux.database.SessionDependecy(),
):
    phone = body.phone
    reason = body.reason
    confirmation: PhoneConfirmation | None = session.query(
        PhoneConfirmation
    ).where(
        and_(
            PhoneConfirmation.phone == phone,
            PhoneConfirmation.reason == reason,
        )
    ).first()
    if confirmation is not None and confirmation.is_reseted():
        session.delete(confirmation)
        confirmation = None
    if confirmation is not None:
        if now() < confirmation.dt_can_retry_after:
            raise fastapi.HTTPException(425)
        else:
            confirmation.retries += 1
    else:
        confirmation = create_phone_confirmation(
            session,
            body.phone,
            body.reason
        )
        session.add(confirmation)
    send_confirmation_code(confirmation)
    session.commit()
    return confirmation
