from apps.core.base_models import BaseModel
from sqlalchemy.orm import mapped_column,Mapped


class User(BaseModel):
    name : Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)

