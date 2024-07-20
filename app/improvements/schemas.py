from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


class SImprovements(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    purchase_date: date
    level: int
    redis_key: str
    image_id: Optional[int] = None
