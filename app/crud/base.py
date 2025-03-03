from typing import Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User

ModelType = TypeVar("ModelType")


class CRUDBase:
    """Базовый класс для операций CRUD с моделями."""

    def __init__(self, model: Type[ModelType]):
        """
        Инициализация CRUD-класса.
        :param model: Модель SQLAlchemy, с которой работает CRUD.
        """
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """
        Получение объекта по его ID.
        :param obj_id: ID объекта.
        :param session: Асинхронная сессия SQLAlchemy.
        :return: Объект или None, если объект не найден.
        """
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        """
        Получение всех объектов.
        :param session: Асинхронная сессия SQLAlchemy.
        :return: Список объектов.
        """
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> ModelType:
        """
        Создание нового объекта.
        :param obj_in: Данные для создания объекта.
        :param session: Асинхронная сессия SQLAlchemy.
        :param user: Пользователь, создающий объект (опционально).
        :return: Созданный объект.
        """
        obj_data = obj_in.dict()
        if user is not None:
            obj_data["user_id"] = user.id
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in,
        session: AsyncSession,
    ) -> ModelType:
        """
        Обновление данных объекта.
        :param db_obj: Объект, который нужно обновить.
        :param obj_in: Новые данные для объекта.
        :param session: Асинхронная сессия SQLAlchemy.
        :return: Обновлённый объект.
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj: ModelType,
        session: AsyncSession,
    ) -> ModelType:
        """
        Удаление объекта.
        :param db_obj: Объект, который нужно удалить.
        :param session: Асинхронная сессия SQLAlchemy.
        :return: Удалённый объект.
        """
        await session.delete(db_obj)
        await session.commit()
        return db_obj
