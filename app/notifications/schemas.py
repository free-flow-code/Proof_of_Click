from datetime import date
from pydantic import BaseModel, ConfigDict


class SNotifications(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    text: str
    send_date: date
