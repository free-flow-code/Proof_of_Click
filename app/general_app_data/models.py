from datetime import datetime
from sqlalchemy import Column, Integer, Float

from app.database import Base


class MiningChance(Base):
    __tablename__ = "mining_chance"

    id = Column(Integer, primary_key=True)
    time_at_calc = Column(Integer, default=datetime.now().timestamp())
    value = Column(Float, nullable=False)

    def __str__(self):
        return f"{datetime.fromtimestamp(self.time_at_calc)} - {self.value}"
