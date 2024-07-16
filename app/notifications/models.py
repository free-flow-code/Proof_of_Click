from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    send_date = Column(Date, nullable=False)

    user = relationship("Users", back_populates="notifications")

    def __str__(self):
        return f"Уведомление пользователю {self.user_id}"
