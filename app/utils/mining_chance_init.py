from app.config import settings


class MiningChanceSingleton:
    _instance = None
    _value = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_value(self):
        if self._value is None:
            raise ValueError("Mining chance is not set.")
        return self._value

    def set_value(self, value):
        self._value = value


def get_mining_chance_singleton():
    return MiningChanceSingleton()


async def set_mining_chance(redis_client):
    """
    Подсчитывает вероятность добычи блока и записывает значение в синглтон.

    Args:
        redis_client: Клиент Redis для взаимодействия с базой данных.

    Returns:
        None
    """
    users_with_balances = await redis_client.zrange("users_balances", 0, -1, withscores=True)
    total_balance = sum(balance for _, balance in users_with_balances)

    mining_chance = round((1 - total_balance / settings.MAX_BLOCKS), 4)
    singleton = get_mining_chance_singleton()
    singleton.set_value(mining_chance)
