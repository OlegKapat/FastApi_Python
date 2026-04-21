from apps.core.base_crud import BaseCrudManagerl
from apps.products.models import Category


class CategoryCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = Category


category_manager = CategoryCrudManager()
