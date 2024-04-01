from fastapi import HTTPException

from app.core.constants import DEFAULT_AMOUNT
from app.models import CharityProject


def check_charity_project_fully_invested(
        project: CharityProject
) -> None:
    if project and project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )


def check_charity_project_before_delete(
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
