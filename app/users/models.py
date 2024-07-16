from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    mail = Column(String, nullable=False, unique=True)
    hash_password = Column(String, nullable=False)
    registration_date = Column(Date, nullable=False)
    referral_link = Column(String, nullable=False)
    referer = Column(ForeignKey("users.id"))
    blocks_balance = Column(Float, default=0.000)  # Пересчитывать в Celery каждые 10 сек., промежуточные данные хранить в Redis, итоговые записывать в БД
    blocks_per_sec = Column(Float, default=0.000)  # Пересчитывать каждый раз при покупке улучшений
    blocks_per_click = Column(Float, default=0.001)  # Пересчитывать каждый раз при покупке умножителя
    improvements = (ForeignKey("improvements.id"))
    telegram_id = Column(Integer)
    last_update_time = Column(Date)

    referred_by = relationship("Users", remote_side=[id], backref="referrals")  # получить список пользователей, привлеченных данным пользователем - user.referrals
    improvement = relationship("Improvements", back_populates="user")
    game_item = relationship("GameItems", back_populates="user")
    notifications = relationship("Notifications", back_populates="user")
    lots_created = relationship("Lots", foreign_keys="[Lots.user_id]", back_populates="user")
    bids_placed = relationship("Lots", foreign_keys="[Lots.best_price_user_id]", back_populates="best_price_user")

    def __str__(self):
        return f"Пользователь {self.username}"
