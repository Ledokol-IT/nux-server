import datetime
import logging
from typing import Literal

import pydantic

import smsaero

logger = logging.getLogger(__name__)

_sms_aero: None | smsaero.SmsAero = None


def setup_sms(smsaero_email, smsaero_apikey):
    global _sms_aero
    _sms_aero = smsaero.SmsAero(smsaero_email, smsaero_apikey)
    try:
        _sms_aero.auth()
    except smsaero.SmsAeroError as e:
        logger.error("SmsAero not initialized")
        logger.exception(e)
        _sms_aero = None
        return


"""
{'data': {'channel': 'FREE SIGN',
          'cost': 3.69,
          'dateCreate': 1658559852,
          'dateSend': 1658559852,
          'extendStatus': 'moderation',
          'from': 'Sms Aero',
          'id': 442437289,
          'number': '79069469277',
          'status': 8,
          'text': 'test 7'},
 'message': None,
 'success': True}


{'data': {'channel': 'FREE SIGN',
          'cost': '3.69',
          'dateAnswer': 1658560024,
          'dateCreate': 1658559852,
          'dateSend': 1658559852,
          'extendStatus': 'delivery',
          'from': 'Sms Aero',
          'id': 442437289,
          'number': 79069469277,
          'status': 1,
          'text': 'test 7'},
 'message': None,
 'success': True}
"""


class MessageStatus(pydantic.BaseModel):
    channel: str | None
    cost: float | None

    @pydantic.validator("cost", pre=True)
    def cost_to_float(cls, v):
        if isinstance(v, str):
            return float(v)
    dateCreate: datetime.datetime | None
    dateSend: datetime.datetime | None

    @pydantic.validator("dateCreate", "dateSend", pre=True, allow_reuse=True)
    def cost_to_datetime(cls, v):
        if v is None:
            return v
        return datetime.datetime.fromtimestamp(v)
    extendStatus: str | None
    from_: str | None = pydantic.Field(alias='from')
    id: int
    phone: int = pydantic.Field(alias='number')
    status: Literal[0, 1, 2, 3, 4, 6, 8]
    text: str | None


def send_message(phone, text):
    if _sms_aero is None:
        logging.warning("SmsAero not available, message not send\n"
                        f"Phone: {phone}\n{text}")
        return
    response = _sms_aero.send(phone, text)
    return MessageStatus(**response['data'])


def send_confirmation_code(phone, code):
    text = """LEDOKOL: {0} your code."""
    return send_message(phone, text.format(code))
