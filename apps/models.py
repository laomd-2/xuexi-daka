from sqlalchemy import *
from core import Base


class Sharing(Base):
    __tablename__ = 'sharing'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    title = Column(String(50))
    thinking = Column(Text)
    time = Column(DateTime, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('name', 'title', sqlite_on_conflict='FAIL'),
        #UniqueConstraint('thinking', sqlite_on_conflict='FAIL')
    )