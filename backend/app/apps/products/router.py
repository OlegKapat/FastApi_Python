from typing import Annotated

from apps.auth.dependencies import require_permision
from apps.core.dependencies import get_async_session
from apps.core.schemas import SearchParamSchema
from apps.users.constants import UserPermisionEnum
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import Category, category_manager
from .schemas import (
    NewCategory,
    PaginatorSavedCategoryResponseSchema,
    SavedCategorySchema,
)

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


@router_categories.get("/{id}", response_model=SavedCategorySchema)
async def get_category_by_id(
    category_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    saved_category = await category_manager.get(
        field_value=category_id, field=Category.id, session=session
    )
    if not saved_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )
    return saved_category


@router_categories.get("/")
async def get_categories(
    params: Annotated[SearchParamSchema, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> PaginatorSavedCategoryResponseSchema:
    result = await category_manager.get_items_pagineted(
        session=session,
        search_fields=[Category.name],
        targeted_shema=SavedCategorySchema,
        params=params,
    )
    return result
