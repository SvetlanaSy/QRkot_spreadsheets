from datetime import datetime
from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BothModel


def close_obj(obj: Type[BothModel]) -> BothModel:
    obj.invested_amount = obj.full_amount
    obj.fully_invested = True
    obj.close_date = datetime.now()
    return obj


def calculate_invested_amount(obj_in, obj):
    available = obj_in.full_amount - obj_in.invested_amount
    expected = obj.full_amount - obj.invested_amount
    if expected == available:
        obj_in = close_obj(obj_in)
        obj = close_obj(obj)
    if available > expected:
        obj_in.invested_amount += expected
        obj = close_obj(obj)
    if available < expected:
        obj.invested_amount += available
        obj_in = close_obj(obj_in)
    return obj_in, obj


async def investing(
        obj_in: Type[BothModel],
        model: Type[BothModel],
        session: AsyncSession,
) -> None:
    open_objs = await session.execute(select(model).where(
        model.fully_invested == 0
    ).order_by(model.create_date))
    open_objs = open_objs.scalars().all()
    for obj in open_objs:
        obj_in, obj = calculate_invested_amount(obj_in, obj)
        session.add(obj_in)
        session.add(obj)
    await session.commit()
    await session.refresh(obj_in)
    return obj_in
