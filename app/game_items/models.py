from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.lots.models import Lots


class GameItems(Base):
    __tablename__ = "game_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    date_at_mine = Column(Date, nullable=False)
    redis_key = Column(String, nullable=False, index=True)
    image_id = Column(Integer)

    lots_it_item = relationship("Lots", back_populates="this_lot_game_item", cascade="all, delete-orphan")

    def __str__(self):
        return f"Игровой предмет {self.name}"
