from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


class SGameItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    date_at_mine: date
    redis_key: str
    image_id: Optional[int] = None
