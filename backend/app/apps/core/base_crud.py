from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError
from typing import Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import and_, asc, delete, desc, exists, func, or_, select, update
from apps.core.base_models import BaseModel


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

    async def patch(self, instance_id: int, session: AsyncSession, data_to_patch: BaseModel,
                    exclude_unset: bool = True) -> BaseModel:
        query = select(self.model).filter(self.model.id == instance_id).with_for_update(nowait=True)
        try:
            result = await session.execute(query)
            item = result.scalars().one_or_none()
        except DBAPIError as e:
            if e.orig.args[0] in (1205, 1213):  # MySQL lock wait timeout and deadlock
                raise HTTPException(status_code=status.HTTP_423_LOCKED,
                                    detail=f"{self.model.__name__} with id {instance_id} locked try again later")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"{self.model.__name__} with id {instance_id} not found")

        data_for_updating: dict = data_to_patch.model_dump(exclude={"id"})
        if not data_for_updating:
            return item

        query = update(self.model).where(self.model.id == instance_id).values(**data_for_updating)
        await session.execute(query)
        await session.commit()
        return item
