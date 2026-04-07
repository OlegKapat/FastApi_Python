from fastapi import APIRouter, Header, Depends
from fastapi.security import OAuth2PasswordRequestForm
from apps.core.dependencies import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import LoginResposeSchema
from apps.auth.auth_handler import auth_handler

router_auth = APIRouter()


@router_auth.post("/login")
async def login(
        request: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session),
) -> LoginResposeSchema:
    login_response: LoginResposeSchema = await auth_handler.get_login_token(session, request)

    return login_response


@router_auth.post("/refresh")
async def refresh_user_token(refresh_token: str = Header(alias='X-Refresh-Token'),
                             session: AsyncSession = Depends(get_async_session)) -> LoginResposeSchema:
    token_pair = await auth_handler.get_refresh_token_pair(refresh_token=refresh_token, session=session)
    return token_pair
