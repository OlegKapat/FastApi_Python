from typing import Callable
from enum import StrEnum
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from apps.core.dependencies import get_async_session
from apps.users.models import User
from apps.users.crud import user_manager
from .auth_handler import auth_handler


class SecurityHandler:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(SecurityHandler.oauth2_scheme),
                           session: AsyncSession = Depends(get_async_session)) -> User:
    # Here you would implement the logic to decode the token and retrieve the user
    # For example, you might use a JWT library to decode the token and verify its validity
    # Then you would query your database to get the user associated with the token
    # If the token is invalid or expired, you would raise an HTTPException
    payload = await auth_handler.decode_token(token)
    if payload.get("key"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token was given")
    user: User | None = await user_manager.get(session=session, field_value=int(payload["sub"]), field=User.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with given email not found")
    if user.use_token_since and user.use_token_since > payload["iat"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User forced logout")
    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.is_admin:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Admin user is required")


def require_permision(required_permision: list[StrEnum]) -> Callable:
    async def permission_dependency(user: User = Depends(get_current_user)) -> User:
        if user.is_admin:
            return user
        user_permision = set(user.permissions)
        required_permision_set: set[str] = {perm.value for perm in required_permision}
        if required_permision_set.issubset(user_permision):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Permissions {', '.join(required_permision_set)} required")

    return permission_dependency
