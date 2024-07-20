from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Lots(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date_at_create = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    game_item_id = Column(ForeignKey("game_items.id", ondelete="CASCADE"), nullable=False)
    start_price = Column(Float, nullable=False)
    best_price = Column(Float)
    best_price_user_id = Column(ForeignKey("users.id"))

    this_lot_game_item = relationship("GameItems", back_populates="lots_it_item", cascade="all")

    def __str__(self):
        return f"Лот №{self.id}"
