from sqlalchemy import *
from core import Base


class Sharing(Base):
    __tablename__ = 'sharing'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    title = Column(String(100))
    thinking = Column(Text)
    time = Column(TIMESTAMP, nullable=False, index=True)