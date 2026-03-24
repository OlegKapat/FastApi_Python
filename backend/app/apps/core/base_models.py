from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapper, mapped_column, declared_attr, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.sql import func

class BaseModel(AsyncAttrs,DeclarativeBase):
    """в базі не створювалась таблиця base"""
    __abstract__ = True

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at:Mapped[datetime] = mapped_column(default=func.now())
    updated_at:Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
