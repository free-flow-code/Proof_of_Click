from app.dao.base import BaseDAO
from app.notifications.models import Notifications


class NotificationsDAO(BaseDAO):
    model = Notifications
