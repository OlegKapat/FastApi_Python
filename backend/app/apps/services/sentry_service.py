from fastapi import HTTPException, status
from sentry_sdk import capture_message
from typing import NoReturn
from settings import settings
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk
import logging


def capture_error(message: str, user_massage: str = "General error. Call support") -> NoReturn:
    capture_message(message, level="error")
    raise HTTPException(detail=user_massage, status_code=status.HTTP_400_BAD_REQUEST)


def init_sentry():
    sentry_logging = LoggingIntegration(event_level=logging.ERROR)
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        send_default_pii=True,
        integrations=[sentry_logging],
    )
