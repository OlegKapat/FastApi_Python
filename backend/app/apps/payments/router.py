import stripe
from apps.core.dependencies import get_async_session
from apps.payments.schemas import PaymentUrlSchema, SetOrderToClosedSchema
from apps.products.dependencies import Order, get_order, order_manager
from apps.users.crud import User, user_manager
from fastapi import APIRouter, Depends, HTTPException, Request, status
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

stripe.api_key = settings.STRIPE_SECRET_KEY

payment_router = APIRouter()


@payment_router.get("/get-payments-url", tags=["payments-url"])
async def get_payments_url(
    request: Request, order: Order = Depends(get_order)
) -> PaymentUrlSchema:
    if order.cost < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough funds"
        )
    order = await order_manager.get_order_with_product(order, None)
    line_items: list[dict] = [
        {
            "price_data": {
                "currency": "uah",
                "product_data": {
                    "name": order_product.product.title,
                    "description": order_product.product.description,
                    "images": [order_product.product.main_image]
                    + order_product.product.images,
                },
                "unit_amount": int(order_product.price * 100),
            },
            "quantity": order_product.quantity,
        }
        for order_product in order.products
    ]
    session_stripe: dict = stripe.checkout.Session.create(
        line_items=line_items,
        mode="payment",
        success_url=request.base_url,
        payment_method_types=["card"],
        cancel_url=f"{request.base_url}scalar",
        customer_email=order.user.email,
        locale="ru",
        metadata={"user_id": order.user.id, "total": order.cost, "order_id": order.id},
    )
    return PaymentUrlSchema(url=session_stripe["url"])


@payment_router.post("/webhook", tags=["webhook"], include_in_schema=settings.DEBUG)
async def stripe_payment_webhook(
    stripe_data: dict,
    session: AsyncSession = Depends(get_async_session),
):
    if not stripe_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided"
        )
    try:
        event = stripe.Event.construct_from(stripe_data, stripe.api_key)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            detail="NO STRIPE DATA", status_code=status.HTTP_400_BAD_REQUEST
        )
    if not event["type"] == "checkout.session.completed":
        return
    user_id = int(event["data"]["object"]["metadata"]["user_id"])
    user = await user_manager.get(session=session, field=User.id, field_value=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )
    order = await order_manager.get_or_create_order(
        user_id=user_id, is_closed=False, session=session
    )
    if order.id != int(event["data"]["object"]["metadata"]["order_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    paid = float(stripe_data["data"]["object"]["amount_total"]) / 100
    if order.cost != paid:
        raise ValueError("order cost is not equal paid amount")
    await order_manager.patch(
        instance_id=order.id,
        session=session,
        data_to_patch=SetOrderToClosedSchema(),
        exclude_unset=False,
    )
    return {f"{order.id=} closed": True}
