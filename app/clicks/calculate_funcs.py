import numpy as np
from datetime import datetime
from app.game_items.dao import GameItemsDAO


def check_item_drop(n_clicks: int, drop_chance: float) -> int:
    """Генерация количества выпавших предметов за n кликов."""
    items_dropped = np.random.binomial(n_clicks, drop_chance)
    return items_dropped


async def calculate_items_won(user_id: int, items_registry, clicks: int, redis_client):
    """"Подсчитывает количество выпавших игровых предметов"""
    for item_key, item_details in items_registry.get_all_items().items():
        current_quantity = await redis_client.hget(f"{item_key}", "current_quantity")
        if int(current_quantity) < item_details.get_value("maximum_amount"):
            number_items_won = check_item_drop(clicks, float(item_details.get_value("drop_chance")))

            if not number_items_won:
                return
            for item in range(number_items_won):
                await GameItemsDAO.add(
                    user_id=user_id,
                    name=item_key,
                    date_at_mine=datetime.utcnow(),
                    redis_key=item_key,
                    image_id=item_details.get_value("image_id")
                )
                await redis_client.hset(f"{item_key}", mapping={"current_quantity": int(current_quantity) + 1})
