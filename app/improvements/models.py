from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base


# Boosts
class Improvements(Base):
    __tablename__ = "improvements"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    purchase_date = Column(Date, nullable=False)
    level = Column(Integer, nullable=False)
    redis_key = Column(String, nullable=False)
    image_id = Column(Integer)

    def __str__(self):
        return f"Улучшение {self.name}"
