from sqlalchemy import Column, String, Text

from app.core.constants import MAX_NAME_LENGTH
from .base import BothModel


class CharityProject(BothModel):
    name = Column(String(MAX_NAME_LENGTH), unique=True, nullable=False)
    description = Column(Text, nullable=False)
