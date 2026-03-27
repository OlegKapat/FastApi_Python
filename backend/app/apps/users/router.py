from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import RegisteredUserSchema,ResponseUserSchema
from apps.core.dependencies import get_async_session
from .crud import user_manager

router_users = APIRouter()


@router_users.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseUserSchema)
async def create_user(user: RegisteredUserSchema,
                      session: AsyncSession = Depends(get_async_session)):
    created_user = await user_manager.create_user(new_user=user, session=session)
    return created_user


