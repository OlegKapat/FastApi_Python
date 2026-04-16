from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer
from apps.core.base_models import BaseModel
import datetime as dt


class Category(BaseModel):
    __tablename__ = 'categories'

    name : Mapped[str]= mapped_column(String,unique=True,nullable=False)
    version: Mapped[int] = mapped_column(Integer,nullable=False,default=1)

    def __str__(self)->str:
        return f"<Category {self.name} - #{self.id}>"