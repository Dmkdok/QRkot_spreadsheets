from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_unique(
    name: str,
    session: AsyncSession,
    project_id: Optional[int] = None,
) -> None:
    """
    Проверяет уникальность имени проекта.
    """
    existing_project = await charity_project_crud.get_project_id_by_name(
        name, session, project_id
    )
    if existing_project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Проект с таким именем уже существует!",
        )


async def check_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """
    Проверяет существование проекта по ID.
    """
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден.",
        )
    return project


def check_project_open(
    project: CharityProject,
) -> None:
    """
    Проверяет, что проект не закрыт.
    """
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Закрытый проект нельзя редактировать!",
        )


def check_amount_sufficiency(
    project: CharityProject,
    new_amount: Optional[int] = None,
) -> None:
    """
    Проверяет, что новая сумма не меньше уже внесённой.
    """
    if new_amount is not None and new_amount < project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=(
                "Нельзя установить сумму меньше уже вложенной:"
                f"{project.invested_amount}."
            ),
        )


def check_no_investments(
    project: CharityProject,
) -> None:
    """
    Проверяет, что в проект не внесены средства.
    """
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="В проект были внесены средства, его нельзя удалить!",
        )
