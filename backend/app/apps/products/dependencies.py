from apps.auth.dependencies import get_current_user
from apps.core.dependencies import get_async_session
from apps.products.crud import Order, order_manager, product_manager
from apps.products.models import Product
from apps.users.models import User
from fastapi import Body, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

ALLOWED_IMAGE_EXTENSIONS = set(
    ["image/jpg", "image/jpeg", "image/png", "image/gif", "image/bmp", "video/mp4"]
)
MAX_FILE_SIZE = 5 * 1024 * 1024


async def validate_image(image: UploadFile = File(...)) -> UploadFile:
    if image.content_type not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg, jpeg, or png images are allowed",
        )

    file_size = len(await image.read())
    await image.seek(0)  # Reset the file pointer after reading

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large max{MAX_FILE_SIZE} bytes",
        )

    return image


async def validate_images(
    images: list[UploadFile] = File(default=None, max_length=10),
) -> list[UploadFile]:
    if not images:
        return []
    if len(images) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 10 images allowed"
        )
    for image in images:
        validate_image(image)
    return images


async def get_order(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Order:
    return await order_manager.get_or_create_order(
        session=session, user_id=user.id, is_closed=False
    )


async def get_products(
    product_id: int = Body(ge=1), session: AsyncSession = Depends(get_async_session)
) -> Product:
    product = await product_manager.get(
        session=session,
        field=Product.id,
        field_value=product_id,
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product
