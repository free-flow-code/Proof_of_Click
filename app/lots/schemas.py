from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


class SLots(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_at_create: date
    expiration_date: date
    game_item_id: int
    start_price: float
    best_price: Optional[float]
    best_price_user_id: Optional[int]
