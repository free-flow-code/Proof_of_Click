import numpy as np
from typing import Optional
from app.tasks.tasks import add_items_to_db
from app.utils.game_items_init import get_items_registry


async def calculate_items_won(user_id: int, count_clicks: int, redis_client) -> Optional[int]:
    """
    Подсчитывает количество выпавших игровых предметов для пользователя и обновляет данные в Redis.

    Args:
        user_id (int): Идентификатор пользователя, для которого вычисляются выпавшие предметы.
        count_clicks (int): Количество кликов, совершённых пользователем.
        redis_client: Клиент Redis для взаимодействия с базой данных.

    Returns:
        Optional[int]: Общее количество выпавших предметов или None, если предметы не выпали.

    Notes:
        - Проверяется шанс выпадения для каждого предмета.
        - Если общее количество выпавших предметов превышает максимум, предмет больше не учитывается.
        - Обновления количества предметов и их добавление в базу данных происходят асинхронно.
    """
    item_quantities = await redis_client.hgetall("item_quantities")
    items_registry = await get_items_registry()
    updates = {}
    total_won = 0

    for item_key, item_details in items_registry.get_all_items().items():
        # уточняем, количество уже выпавших предметов и его ограничение
        current_quantity = int(item_quantities.get(item_key, 0))
        max_quantity = item_details.get_value("maximum_amount")
        if current_quantity >= max_quantity:
            items_registry.delete_item(item_key)
            continue

        # вычисляем количество выпавших предметов на основе шанса
        drop_chance = float(item_details.get_value("drop_chance"))
        won_items = np.random.binomial(count_clicks, drop_chance)

        if won_items:
            updates[item_key] = current_quantity + won_items
            total_won += won_items

            add_items_to_db.delay(
                user_id=user_id,
                item_key=item_key,
                items_count=won_items,
                image_id=item_details.get_value("image_id")
            )

    if updates:
        await redis_client.hmset("item_quantities", updates)

    return total_won
