from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from apps.core.dependencies import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.crud import user_manager
from apps.users.models import User

router_auth = APIRouter()


@router_auth.post("/login")
async def login(
    request: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_manager.get(
        session=session,
        field_value=request.username,
        field=User.email,
    )
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect username or password")

    return {"access_token": "fake-token-for-{}".format(request.username), "token_type": "bearer"}
