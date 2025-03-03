from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    """CRUD-класс для работы с благотворительными проектами."""

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
        project_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Получение ID проекта по его названию.
        :param project_name: Название проекта.
        :param session: Асинхронная сессия SQLAlchemy.
        :param project_id: ID проекта, который исключается из поиска
        (для обновления).
        :return: ID проекта или None, если проект не найден.
        """
        query = select(CharityProject.id).where(
            CharityProject.name == project_name
        )
        if project_id:
            query = query.where(CharityProject.id != project_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_open_projects(
        self,
        session: AsyncSession,
    ) -> List[CharityProject]:
        """
        Получает все незакрытые проекты, отсортированные по дате создания.

        :param session: Асинхронная сессия SQLAlchemy.
        :return: Список незакрытых проектов.
        """
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(False))
            .order_by(CharityProject.create_date)
        )
        return result.scalars().all()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> List[CharityProject]:
        """
        Получает все закрытые проекты, отсортированные по времени сбора средств
        (от меньшего к большему).

        :param session: Асинхронная сессия SQLAlchemy.
        :return: Список закрытых проектов, отсортированных по скорости сбора.
        """
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(True))
            .order_by(
                (CharityProject.close_date - CharityProject.create_date).asc()
            )
        )
        return result.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
