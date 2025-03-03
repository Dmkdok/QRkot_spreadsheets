from sqlalchemy import Column, String, Text

from app.models.base import BaseModel


class CharityProject(BaseModel):
    """Модель благотворительного проекта."""

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
