from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseModel


class Donation(BaseModel):
    """Модель пожертвования."""

    comment = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
