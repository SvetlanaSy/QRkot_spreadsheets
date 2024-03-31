from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_project_crud


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


def check_full_amount(
    full_amount: int,
    invested_amount: int
) -> None:
    if full_amount < invested_amount:
        raise HTTPException(
            status_code=400,
            detail='Требуемая сумма не может быть меньше уже внесённой суммы!'
        )
