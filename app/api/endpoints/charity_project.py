from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_amount_sufficiency,
    check_name_unique,
    check_no_investments,
    check_project_exists,
    check_project_open,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import Donation
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import investment_process

router = APIRouter()


@router.post(
    "/",
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    project_data: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создаёт благотворительный проект.

    Только для суперюзеров.
    """
    await check_name_unique(project_data.name, session)
    new_project = await charity_project_crud.create(project_data, session)
    new_project = await investment_process(new_project, Donation, session)
    return new_project


@router.get(
    "/",
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех проектов.
    """
    projects = await charity_project_crud.get_multi(session)
    return projects


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    project_data: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.

    Редактирование проекта.
    Закрытый проект нельзя редактировать.
    Нельзя установить требуемую сумму меньше уже вложенной.
    """
    project = await check_project_exists(project_id, session)
    check_project_open(project)

    if project_data.name:
        await check_name_unique(project_data.name, session, project_id)
    if project_data.full_amount is not None:
        check_amount_sufficiency(project, project_data.full_amount)
    updated_project = await charity_project_crud.update(
        project, project_data, session
    )
    updated_project = await investment_process(
        updated_project, Donation, session
    )
    return updated_project


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.

    Удаляет проект. Нельзя удалить проект,
    в который уже были инвестированы средства,
    его можно только закрыть.
    """
    project = await check_project_exists(project_id, session)
    check_no_investments(project)
    deleted_project = await charity_project_crud.remove(project, session)
    return deleted_project
