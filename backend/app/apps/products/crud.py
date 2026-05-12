from apps.core.base_crud import BaseCrudManagerl
from apps.products.models import Category, Product


class CategoryCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Category


class ProductCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Product


category_manager = CategoryCrudManager()
product_manager = ProductCrudManager()
