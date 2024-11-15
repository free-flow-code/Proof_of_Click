import logging
import json
from datetime import date

from app.users.models import UserRole
from app.users.dao import UsersDAO


def sanitize_dict_for_redis(user_data: dict) -> dict:
    """Заменяет НЕ поддерживаемые в redis типы данных, из значений словаря, на поддерживаемые."""
    return {
        k: (
            v.strftime('%Y-%m-%d') if isinstance(v, date) else
            # add "v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else" for last_update_time
            v.value if isinstance(v, UserRole) else
            str(v) if isinstance(v, bool) else
            str(v) if isinstance(v, list) else
            (v if v is not None else '')
        )
        for k, v in user_data.items()
    }


async def load_boosts(redis_client):
    """Загружает игровые улучшения в redis.

    Все значения находятся в boost:{boost_name}:data и сериализованы с помощью json.dumps.
    """
    name_boosts = []
    with open("app/boosts.json", "r", encoding="utf-8") as file:
        boosts = json.loads(file.read())
        for boost in boosts:
            for boost_name, boost_details in boost.items():
                boost_data = {
                    f"{boost_name}": {
                        f"{detail_key}": sanitize_dict_for_redis(detail_data) if detail_key == "levels" else detail_data
                        for detail_key, detail_data in boost_details.items()
                    }
                }
                max_levels = {"max_levels": len(boost_data[f"{boost_name}"]["levels"])}
                boost_data[f"{boost_name}"].update(max_levels)
                name_boosts.append(boost_name)

                # Сериализация словаря в JSON строку перед сохранением в Redis
                serialized_boost_data = json.dumps(boost_data[f"{boost_name}"])
                await redis_client.hset(f"boost:{boost_name}", mapping={"data": serialized_boost_data})
    await redis_client.set("name_boosts", json.dumps(name_boosts))
    logging.info("Boosts loads successful to redis")


async def add_user_data_to_redis(user_data: dict, redis_client):
    await redis_client.zadd("users_balances", {f"{user_data.get('username')}": user_data.get("blocks_balance", 0.0)})
    user_id = user_data.get("id")
    await redis_client.hset(f"user_data:{user_id}", mapping=user_data)
    await redis_client.expire(f"user_data:{user_id}", 3600)


async def load_all_users_balances(redis_client):
    """Загружает топ 100 балансов пользователей в redis из БД."""
    top_users = await UsersDAO.get_top_100_users()
    for user in top_users:
        await redis_client.zadd("users_balances", {f"{user.get('username')}": user.get("blocks_balance", 0.0)})
