import uuid
from typing import Annotated

from apps.auth.dependencies import require_permision
from apps.core.dependencies import get_async_session
from apps.core.schemas import SearchParamSchema
from apps.products.models import Product
from apps.storage.s3 import s3_storage
from apps.users.constants import UserPermisionEnum
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import Category, category_manager, product_manager
from .schemas import (
    NewCategory,
    PaginatorSavedCategoryResponseSchema,
    PatchCategorySchema,
    SavedCategorySchema,
    SavedProductSchema,
)

router_categories = APIRouter()
router_product = APIRouter()


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


@router_categories.patch(
    "/{id}",
    dependencies=[Depends(require_permision([UserPermisionEnum.CAN_CREATE_CATERGORY]))],
)
async def update_category(
    patch_data: PatchCategorySchema,
    category_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
) -> SavedCategorySchema:
    update_category = await category_manager.patch(
        instance_id=category_id, data_to_patch=patch_data, session=session
    )
    return update_category


@router_categories.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permision([UserPermisionEnum.CAN_CREATE_CATERGORY]))],
)
async def delete_category(
    category_id: int = Path(..., description="The id of the item", ge=1, alias="id"),
    session: AsyncSession = Depends(get_async_session),
):
    await category_manager.delete_item(instance_id=category_id, session=session)


@router_product.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permision([UserPermisionEnum.CAN_CREATE_PRODUCT]))],
)
async def create_product(
    title: str = Form(min_length=3, max_length=200),
    description: str = Form(min_length=3, max_length=200),
    price: float = Form(ge=0.01),
    category_id: int = Form(gt=0),
    main_image: UploadFile = File(...),
    images: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
) -> SavedProductSchema:
    is_category_exist = await category_manager.item_exist(
        field=Category.id, field_value=category_id, session=session
    )

    if not is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist",
        )
    is_product_exist = await product_manager.item_exist(
        field=Product.title, field_value=title.strip(), session=session
    )
    if is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with title {title} already exists",
        )
    product_uuid = uuid.uuid4()
    try:
        main_image_url = await s3_storage.upload_file_to_s3(
            files=main_image, uuid_obj=product_uuid, return_first=True
        )
        image_url = await s3_storage.upload_file_to_s3(
            files=images, uuid_obj=product_uuid
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail=f"Failed to upload main image: {str(e)}",
        )

    created_product = await product_manager.create(
        title=title.strip(),
        description=description.strip(),
        price=price,
        images=image_url,
        main_image=main_image_url,
        category_id=category_id,
        session=session,
    )
    return SavedProductSchema.from_orm(created_product)
