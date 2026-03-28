from datetime import datetime
from logging import root

from sqlalchemy.orm import DeclarativeBase, Mapper, mapped_column, declared_attr, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker,AsyncSession
from sqlalchemy.sql import func
from settings import settings

engine = create_async_engine(settings.DATABASE_ASYNC_URL, future=True, echo=settings.DEBUG,
                             pool_size=settings.DATABASE_POOL_SIZE, max_overflow=settings.DATABASE_MAX_OVERFLOW,
                             pool_pre_ping=True,pool_recycle=settings.DATABASE_POOL_RECYCLE)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False,class_=AsyncSession)


class BaseModel(AsyncAttrs, DeclarativeBase):
    """в базі не створювалась таблиця base"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
