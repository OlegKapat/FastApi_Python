from apps.core.base_crud import BaseCrudManagerl
from apps.products.models import Category, Order, Product


class CategoryCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Category


class ProductCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Product


class OrderCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Order


category_manager = CategoryCrudManager()
product_manager = ProductCrudManager()
order_manager = OrderCrudManager()
