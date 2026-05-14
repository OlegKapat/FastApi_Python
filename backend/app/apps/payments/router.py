import stripe
from apps.payments.schemas import PaymentUrlSchema
from apps.products.dependencies import Order, get_order, order_manager
from fastapi import APIRouter, Depends, HTTPException, Request, status
from settings import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

payment_router = APIRouter()


@payment_router.post("/get-payments-url", tags=["payments-url"])
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
