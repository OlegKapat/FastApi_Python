from abc import ABC, abstractmethod
from math import ceil
from typing import Any, Optional

from apps.core.base_models import BaseModel
from fastapi import HTTPException, status
from sqlalchemy import and_, asc, delete, desc, exists, func, or_, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from .schemas import PaginationResponseSchema, SearchParamSchema, SortEnum


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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error has occurred while creating {self.model} instance with {kwargs}, {e=}",
            )
        finally:
            await session.close()

    async def get(
        self, session: AsyncSession, field_value: Any, field: InstrumentedAttribute
    ) -> Optional[BaseModel]:
        query = select(self.model).filter(field == field_value)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def patch(
        self,
        instance_id: int,
        session: AsyncSession,
        data_to_patch: BaseModel,
        exclude_unset: bool = True,
    ) -> BaseModel:
        query = (
            select(self.model)
            .filter(self.model.id == instance_id)
            .with_for_update(nowait=True)
        )
        try:
            result = await session.execute(query)
            item = result.scalars().one_or_none()
        except DBAPIError as e:
            if e.orig.args[0] in (1205, 1213):  # MySQL lock wait timeout and deadlock
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"{self.model.__name__} with id {instance_id} locked try again later",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {instance_id} not found",
            )

        data_for_updating: dict = data_to_patch.model_dump(exclude={"id"})
        if not data_for_updating:
            return item

        optimistic_offline_lock_version = getattr(item, "version", None)
        if optimistic_offline_lock_version is not None:
            if optimistic_offline_lock_version != getattr(
                data_to_patch, "version", None
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"{self.model.__name__} with id {instance_id} has been modified by another process",
                )
            data_for_updating["version"] = optimistic_offline_lock_version + 1

        query = (
            update(self.model)
            .where(self.model.id == instance_id)
            .values(**data_for_updating)
        )
        await session.execute(query)
        await session.commit()
        return item

    async def get_items_pagineted(
        self,
        *,
        session: AsyncSession,
        params: SearchParamSchema,
        targeted_shema: type[BaseModel],
        search_fields: list[InstrumentedAttribute],
    ):
        sort_direction = asc if params.sort_direction == SortEnum.ASC else desc
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if params.q and search_fields:
            if params.use_sharp_filter:
                search_field_condition = or_(
                    func.lower(search_field) == params.q.lower()
                    for search_field in search_fields
                )
            else:
                words = [word for word in params.q.split() if len(word) > 1]
                search_field_condition = or_(
                    and_(*(search_field.icontains(word) for word in words))
                    for search_field in search_fields
                )
            query = query.filter(search_field_condition)
            count_query = count_query.filter(search_field_condition)

            sort_field = getattr(self.model, params.sort_by, self.model.id)
            query = query.order_by(sort_direction(sort_field))
            offset = (params.page - 1) * params.limit
            query = query.offset(offset).limit(params.limit)

        result = await session.execute(query)
        result_count = await session.execute(count_query)
        total_count: int = result_count.scalar()

        return PaginationResponseSchema(
            items=[targeted_shema.from_orm(item) for item in result.scalars().all()],
            total=total_count,
            page=params.page,
            limit=params.limit,
            pages=ceil(total_count / params.limit),
        )

    async def item_exist(
        self, *, session: AsyncSession, field_value: Any, field: InstrumentedAttribute
    ) -> bool:
        query = select(exists().where(field == field_value))
        result = await session.execute(query)
        return result.scalar()

    async def delete_item(self, instance_id: int, session: AsyncSession) -> None:
        is_item_exist = await self.item_exist(
            session=session, field=self.model.id, field_value=instance_id
        )
        if not is_item_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {instance_id} not found",
            )

        query = delete(self.model).where(self.model.id == instance_id)
        await session.execute(query)
        await session.commit()

    async def get_or_create_order(
        self,
        session: AsyncSession,
        defaults: dict = None,
        **kwargs,
    ) -> Optional[BaseModel]:
        query = select(
            self.model,
        ).filter_by(**kwargs)
        result = await session.execute(query)
        instance = result.scalars().one_or_none()
        if instance:
            return instance
        else:
            instance = self.model(**kwargs, **(defaults or {}))
        session.add(instance)
        try:
            await session.commit()
            await session.refresh(instance)
            return instance
        except IntegrityError:
            await session.rollback()
