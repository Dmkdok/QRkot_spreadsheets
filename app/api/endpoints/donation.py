from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import CharityProject, User
from app.schemas.donation import DonationCreate, DonationDB, DonationDBFull
from app.services.investment import investment_process

router = APIRouter()


@router.post(
    "/",
    response_model=DonationDB,
    response_model_exclude_none=True,
    response_model_exclude={"user_id"},
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Сделать пожертвование.

    Для аутентифицированных пользователей.
    """
    new_donation = await donation_crud.create(donation, session, user)
    new_donation = await investment_process(
        new_donation, CharityProject, session
    )
    return new_donation


@router.get(
    "/",
    response_model=List[DonationDBFull],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получить список всех пожертвований

    Только для суперюзеров.
    """
    donations = await donation_crud.get_multi(session)
    return donations


@router.get(
    "/my",
    response_model=List[DonationDB],
    response_model_exclude={"user_id"},
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Получить список моих пожертвований.

    Для аутентифицированных пользователей.
    """
    donations = await donation_crud.get_by_user(user, session)
    return donations
