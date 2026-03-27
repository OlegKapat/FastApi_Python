from abc import ABC, abstractmethod


from sqlalchemy.ext.asyncio import AsyncSession
from apps.core.base_models import BaseModel
from typing import Optional
from fastapi import HTTPException, status


class BaseCrudManagerl(ABC):
    model: type[BaseModel] = None

    @abstractmethod
    def __init__(self):
        pass

    async def create_instance(self, *, session: AsyncSession, **kwargs) -> Optional[BaseModel]:
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
