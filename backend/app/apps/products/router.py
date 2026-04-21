from apps.auth.dependencies import require_permision
from apps.core.dependencies import get_async_session
from apps.users.constants import UserPermisionEnum
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import Category, category_manager
from .schemas import NewCategory, SavedCategorySchema

router_categories = APIRouter()


@router_categories.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permision([UserPermisionEnum.CAN_CREATE_CATERGORY]))],
)
async def create_category(
    new_category: NewCategory, session: AsyncSession = Depends(get_async_session)
) -> SavedCategorySchema:
    maybe_category = await category_manager.get(
        field_value=new_category.name, field=Category.name, session=session
    )
    if maybe_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name {new_category.name} already exists",
        )
    saved_category = await category_manager.create(
        **new_category.model_dump(), session=session
    )
    return saved_category
