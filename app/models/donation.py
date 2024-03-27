from sqlalchemy import Column, Integer, ForeignKey, Text

from .base import BothModel


class Donation(BothModel):
    user_id = Column(Integer, ForeignKey(
        'user.id', name='fk_donation_user_id_user'))
    comment = Column(Text)
