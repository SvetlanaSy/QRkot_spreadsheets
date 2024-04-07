from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_project_or_404
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_project_crud
from app.schemas.charityproject import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate)
from app.services.crud_services import InvestmentManager


router = APIRouter()


@router.get('/',
            response_model=list[CharityProjectDB],)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.post('/',
             response_model=CharityProjectDB,
             response_model_exclude_none=False,
             dependencies=[Depends(current_superuser)],)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    manager = InvestmentManager(session)
    return await manager.create_full_charity_project(charity_project)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=False,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    project = await get_project_or_404(project_id, session)
    manager = InvestmentManager(session)
    return await manager.update_partial_charity_project(project, obj_in)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    project = await get_project_or_404(project_id, session)
    manager = InvestmentManager(session)
    return await manager.remove_charity_project(project)
