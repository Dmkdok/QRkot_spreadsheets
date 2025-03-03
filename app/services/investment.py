from datetime import datetime
from typing import Type, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject, Donation


async def investment_process(
    target: Union[CharityProject, Donation],
    source_model: Type[Union[CharityProject, Donation]],
    session: AsyncSession,
) -> Union[CharityProject, Donation]:
    """
    Распределяет средства между пожертвованиями и проектами по принципу FIFO.

    :param target: Объект, в который инвестируются средства
    (проект или пожертвование).
    :param source_model: Модель источника средств
    (Donation или CharityProject).
    :param session: Асинхронная сессия SQLAlchemy.
    :return: Обновлённый целевой объект.
    """
    if target.fully_invested:
        return target

    if source_model == CharityProject:
        sources = await charity_project_crud.get_open_projects(session)
    else:
        result = await session.execute(
            select(source_model)
            .where(source_model.fully_invested.is_(False))
            .order_by(source_model.create_date)
        )
        sources = result.scalars().all()

    if not sources:
        return target

    target_remaining = target.full_amount - target.invested_amount

    for source in sources:
        source_remaining = source.full_amount - source.invested_amount

        investment_amount = min(target_remaining, source_remaining)

        if investment_amount > 0:
            target.invested_amount += investment_amount
            source.invested_amount += investment_amount

            if target.invested_amount >= target.full_amount:
                target.fully_invested = True
                target.close_date = datetime.now()
                target_remaining = 0
            else:
                target_remaining = target.full_amount - target.invested_amount

            if source.invested_amount >= source.full_amount:
                source.fully_invested = True
                source.close_date = datetime.now()

            session.add(target)
            session.add(source)

            if target.fully_invested:
                break

    await session.commit()
    await session.refresh(target)

    return target
