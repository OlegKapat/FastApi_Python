from fastapi import HTTPException, status
from sentry_sdk import capture_message
from typing import NoReturn


def capture_error(message: str, user_massage: str = "General error. Call support") -> NoReturn:
    capture_message(message, level="error")
    raise HTTPException(detail=user_massage,status_code=status.HTTP_400_BAD_REQUEST)
