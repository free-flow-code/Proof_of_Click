from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Improvements(Base):
    __tablename__ = "improvements"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    purchase_date = Column(Date, nullable=False)
    redis_key = Column(String, nullable=False)
    image_id = Column(Integer)

    user = relationship("Users", back_populates="improvement")

    def __str__(self):
        return f"Улучшение {self.name}"
