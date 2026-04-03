from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from apps.core.base_models import BaseModel
from typing import Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import and_, asc, delete, desc, exists, func, or_, select, update


class BaseCrudManagerl(ABC):
    model: type[BaseModel] = None

    @abstractmethod
    def __init__(self):
        pass

    async def create(self, *, session: AsyncSession, **kwargs) -> Optional[BaseModel]:
        instance = self.model(**kwargs)
        session.add(instance)
        try:
            await session.commit()
            return instance
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        finally:
            await session.close()

    async def get(self, session: AsyncSession, field_value: Any, field: InstrumentedAttribute) -> Optional[BaseModel]:
       query = select(self.model).filter(field == field_value)
       result = await session.execute(query)
       return result.scalar_one_or_none()