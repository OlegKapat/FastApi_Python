from apps.core.base_crud import BaseCrudManagerl
from apps.products.models import Category, Order, OrderProduct, Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CategoryCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Category


class ProductCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Product


class OrderCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Order

    async def get_order_with_product(
        self,
        order_id: int,
        session: AsyncSession,
    ) -> Order:
        result = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.products).selectinload(OrderProduct.product)
            )
            .filter(self.model.id == order_id)
        )
        order = result.scalars().first()
        if order.products:
            order.products = [p for p in order.products if p.quantity]
        return order


class OrderProductCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = OrderProduct

    async def change_quantity_and_set_current_price(
        self,
        product: Product,
        order: Order,
        quantity: int,
        is_set_quantity_mode: bool,
        session: AsyncSession,
    ) -> None:
        order_product: OrderProduct = await self.get_or_create_order(
            session=session, order_id=order.id, product_id=product.id
        )
        if is_set_quantity_mode:
            order_product.quantity = quantity
        else:
            order_product.quantity += quantity
            if order_product.quantity < 0:
                order_product.quantity = 0
        order_product.price = product.price
        session.add(order_product)
        await session.commit()
        await session.refresh(order_product)
        await session.refresh(order)


category_manager = CategoryCrudManager()
product_manager = ProductCrudManager()
order_manager = OrderCrudManager()
order_product_manager = OrderProductCrudManager()
