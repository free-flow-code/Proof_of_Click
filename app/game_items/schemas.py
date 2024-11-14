from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


class SGameItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    date_at_mine: date
    image_id: Optional[int] = None
