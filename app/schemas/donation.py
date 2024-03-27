from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt
from typing import Optional

from app.core.constants import DEFAULT_AMOUNT


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]


class DonationCreate(DonationBase):
    id: Optional[int]
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationCreate):
    user_id: int
    invested_amount: Optional[int] = Field(DEFAULT_AMOUNT)
    fully_invested: Optional[bool]
    close_date: Optional[datetime]
