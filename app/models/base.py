from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer

from app.core.db import Base


class BaseModel(Base):
    """Абстрактный базовый класс для моделей с общими полями."""

    __abstract__ = True

    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime, default=None, nullable=True)
    fully_invested = Column(Boolean, default=False)
    invested_amount = Column(Integer, default=0)
    full_amount = Column(Integer, nullable=False)
