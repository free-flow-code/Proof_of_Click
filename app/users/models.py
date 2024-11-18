from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from random import randint

from app.database import Base
from app.improvements.models import Improvements
from app.notifications.models import Notifications


class UserRole(enum.Enum):
    user = "user"
    moder = "moder"
    admin = "admin"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    mail = Column(String, nullable=False, unique=True)
    hash_password = Column(String, nullable=False)
    registration_date = Column(Date, nullable=False)
    referral_link = Column(String, nullable=False)
    referer = Column(ForeignKey("users.id", ondelete="SET NULL"))
    blocks_balance = Column(Float, default=0.000)  # Пересчитывать в Celery каждые 10 сек., промежуточные данные хранить в Redis, итоговые записывать в БД
    clicks_per_sec = Column(Float, default=0.000)  # Пересчитывать каждый раз при покупке autoclicker
    blocks_per_click = Column(Float, default=0.001)  # Пересчитывать каждый раз при покупке multiplier
    improvements = Column(JSON, default=[])  # TODO удалить?
    telegram_id = Column(Integer)
    last_update_time = Column(Date)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    mail_confirm_code = Column(Integer, default=randint(100000, 999999))
    is_confirm_mail = Column(Boolean, default=False)

    referred_by = relationship("Users", remote_side=[id], backref="referrals")
    boosts = relationship("Improvements", backref="user", cascade="all, delete-orphan")
    game_items = relationship("GameItems", backref="user", cascade="all, delete-orphan")
    notifications = relationship("Notifications", backref="user", cascade="all, delete-orphan")
    lots_created = relationship("Lots", foreign_keys="[Lots.user_id]", backref="user", cascade="all, delete-orphan")
    bids_placed = relationship("Lots", foreign_keys="[Lots.best_price_user_id]", backref="best_price_user")

    def __str__(self):
        return f"Пользователь {self.username}"
