from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationBase, DonationCreate, DonationDB
from app.services.crud_services import InvestmentManager


router = APIRouter()


@router.get('/',
            response_model=list[DonationDB],
            dependencies=[Depends(current_superuser)],
            )
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    donations = await donation_crud.get_multi(session)
    return donations


@router.post('/',
             response_model=DonationCreate,
             response_model_exclude_none=False,)
async def create_donation(
        donation: DonationBase,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    return await InvestmentManager.create_full_donation(session, donation, user)


@router.get('/my',
            response_model=list[DonationCreate],
            response_model_exclude={'user_id'},
            )
async def get_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """Получает список всех пожертвований для текущего пользователя."""
    donations = await donation_crud.get_by_user(session=session, user=user)
    return donations
