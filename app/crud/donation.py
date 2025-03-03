from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):
    """Класс для CRUD-операций с пожертвованиями."""

    async def get_by_user(
        self,
        user: User,
        session: AsyncSession,
    ) -> List[Donation]:
        """
        Получение всех пожертвований пользователя.
        :param user: Пользователь, чьи пожертвования нужно получить.
        :param session: Асинхронная сессия SQLAlchemy.
        :return: Список пожертвований пользователя.
        """
        result = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return result.scalars().all()


donation_crud = CRUDDonation(Donation)
