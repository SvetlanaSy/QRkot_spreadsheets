from datetime import datetime
from typing import Type

from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_AMOUNT
from app.core.db import get_async_session
from app.crud.charityproject import charity_project_crud
from app.crud.donation import donation_crud
from app.models import Donation, CharityProject
from app.models.base import BothModel


class InvestmentManager:

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    def _close_obj(self, obj: Type[BothModel]) -> BothModel:
        obj.invested_amount = obj.full_amount
        obj.fully_invested = True
        obj.close_date = datetime.now()
        return obj

    def _calculate_invested_amount(self, obj_in, obj):
        available = obj_in.full_amount - obj_in.invested_amount
        expected = obj.full_amount - obj.invested_amount
        if expected == available:
            obj_in = self._close_obj(obj_in)
            obj = self._close_obj(obj)
        if available > expected:
            obj_in.invested_amount += expected
            obj = self._close_obj(obj)
        if available < expected:
            obj.invested_amount += available
            obj_in = self._close_obj(obj_in)
        return obj_in, obj

    async def _investing(
        self,
        obj_in: Type[BothModel],
        model: Type[BothModel],
    ) -> None:
        open_objs = await self.session.execute(select(model).where(
            model.fully_invested == 0
        ).order_by(model.create_date))
        open_objs = open_objs.scalars().all()
        for obj in open_objs:
            obj_in, obj = self._calculate_invested_amount(obj_in, obj)
            self.session.add(obj_in)
            self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj_in)
        return obj_in

    async def _check_name_duplicate(
        self,
        project_name: str,
    ) -> None:
        project = await charity_project_crud.get_project_id_by_name(project_name, self.session)
        if project is not None:
            raise HTTPException(
                status_code=400,
                detail='Проект с таким именем уже существует!')

    def _check_full_amount(
        self,
        full_amount: int,
        invested_amount: int
    ) -> None:
        if full_amount < invested_amount:
            raise HTTPException(
                status_code=400,
                detail='Требуемая сумма не может быть меньше уже внесённой суммы!')

    def _check_charity_project_fully_invested(
            self,
            project: CharityProject
    ) -> None:
        if project and project.fully_invested:
            raise HTTPException(
                status_code=400,
                detail='Закрытый проект нельзя редактировать!')

    def _check_charity_project_before_delete(
            self,
            project: CharityProject
    ) -> None:
        if project.fully_invested:
            raise HTTPException(
                status_code=400,
                detail='В проект были внесены средства, не подлежит удалению!'
            )
        if project.invested_amount != DEFAULT_AMOUNT:
            raise HTTPException(
                status_code=400,
                detail='В проект были внесены средства, не подлежит удалению!'
            )

    async def update_partial_charity_project(self, project, obj_in):
        if obj_in.name != project.name:
            await self._check_name_duplicate(obj_in.name)
        if obj_in.full_amount != project.full_amount:
            self._check_full_amount(
                obj_in.full_amount, project.invested_amount)
        self._check_charity_project_fully_invested(project)
        if project.full_amount == project.invested_amount:
            self._close_obj(project)
        project = await charity_project_crud.update(
            self.session, project, obj_in)
        return project

    async def remove_charity_project(self, project):
        self._check_charity_project_before_delete(
            project)
        await charity_project_crud.remove(
            self.session, project
        )
        return project

    async def create_full_charity_project(self, project):
        await self._check_name_duplicate(project.name)
        new_project = await charity_project_crud.create(self.session, project)
        new_project = await self._investing(new_project, Donation)
        return new_project

    async def create_full_donation(self, donation, user):
        new_donation = await donation_crud.create(
            self.session, donation, user)
        new_donation = await self._investing(new_donation, CharityProject)
        return new_donation
