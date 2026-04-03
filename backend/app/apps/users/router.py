from fastapi import APIRouter, status, Depends, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .schemas import RegisteredUserSchema, ResponseUserSchema
from apps.core.dependencies import get_async_session
from .crud import user_manager
from apps.auth.dependencies import get_current_user, get_admin_user

router_users = APIRouter()


@router_users.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseUserSchema)
async def create_user(user: RegisteredUserSchema,
                      session: AsyncSession = Depends(get_async_session)):
    created_user = await user_manager.create_user(new_user=user, session=session)
    return created_user


@router_users.get("/user-info")
async def get_my_info(user: User = Depends(get_current_user)) -> RegisteredUserSchema:
    return RegisteredUserSchema.model_validate(user)


@router_users.get("/{id}", dependencies=[Depends(get_admin_user)])
async def get_user(user_id: int = Path(..., description="The id of the user", ge=1, alias="id"),
                   session: AsyncSession = Depends(get_async_session)) -> ResponseUserSchema:
    user: User = await user_manager.get(session=session, field_value=user_id, field=User.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ResponseUserSchema.model_validate(user)
