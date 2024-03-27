from fastapi import Query
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

from app.core.constants import DEFAULT_AMOUNT, MAX_NAME_LENGTH, MIN_NAME_LENGTH


class CharityProjectCreate(BaseModel):
    name: str = Query(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    description: str = Query(min_length=MIN_NAME_LENGTH)
    full_amount: PositiveInt


class CharityProjectUpdate(BaseModel):
    name: str = Field(None, min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    description: str = Field(None, min_length=MIN_NAME_LENGTH)
    full_amount: PositiveInt = Field(DEFAULT_AMOUNT)

    class Config:
        extra = Extra.forbid


class CharityProjectDB(CharityProjectUpdate):
    id: int
    invested_amount: int = Field(DEFAULT_AMOUNT)
    fully_invested: bool = Field(False)
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
