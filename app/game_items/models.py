from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class GameItems(Base):
    __tablename__ = "game_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    date_at_mine = Column(Date, nullable=False)
    redis_key = Column(String, nullable=False, index=True)
    image_id = Column(Integer)

    user = relationship("Users", back_populates="game_item")
    lots = relationship("Lots", back_populates="game_item")

    def __str__(self):
        return f"Игровой предмет {self.name}"
