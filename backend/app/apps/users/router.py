from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .schemas import RegisteredUserSchema, ResponseUserSchema
from apps.core.dependencies import get_async_session
from .crud import user_manager
from apps.auth.dependencies import get_current_user

router_users = APIRouter()


@router_users.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseUserSchema)
async def create_user(user: RegisteredUserSchema,
                      session: AsyncSession = Depends(get_async_session)):
    created_user = await user_manager.create_user(new_user=user, session=session)
    return created_user


@router_users.get("/user-info")
async def get_my_info(user:User=Depends(get_current_user) ) -> RegisteredUserSchema:
    return RegisteredUserSchema.model_validate(user)
