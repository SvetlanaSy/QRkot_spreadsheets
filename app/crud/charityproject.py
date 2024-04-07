from fastapi import APIRouter, Depends
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession = Depends(get_async_session),
    ) -> Optional[int]:
        project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        project_id = project_id.scalars().first()
        return project_id

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        projects = await session.execute(
            select([CharityProject.name,
                    CharityProject.close_date,
                    CharityProject.create_date,
                    CharityProject.description]).where(
                CharityProject.fully_invested).order_by(
                func.extract('year', CharityProject.close_date) - func.extract('year', CharityProject.create_date),
                func.extract('month', CharityProject.close_date) - func.extract('month', CharityProject.create_date),
                func.extract('day', CharityProject.close_date) - func.extract('day', CharityProject.create_date)))
        projects = projects.all()
        return projects


charity_project_crud = CRUDCharityProject(CharityProject)
