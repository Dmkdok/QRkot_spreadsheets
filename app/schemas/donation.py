from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]


class DonationDB(DonationCreate):
    id: int
    create_date: datetime
    user_id: int

    class Config:
        orm_mode = True


class DonationDBFull(DonationDB):
    invested_amount: int = Field(0, ge=0)
    close_date: Optional[datetime] = None
    fully_invested: bool = Field(False)

    class Config:
        orm_mode = True
