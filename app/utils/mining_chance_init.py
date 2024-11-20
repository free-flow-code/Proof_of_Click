from app.utils.logger_init import logger
from app.config import settings
from app.redis_init import get_redis


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


def get_mining_chance_singleton() -> MiningChanceSingleton:
    return MiningChanceSingleton()


async def set_mining_chance() -> None:
    """
    Берет сумму балансов всех пользователей из Redis ("users_balances:{REDIS_NODE_TAG_3}"),
    подсчитывает вероятность добычи блока и записывает значение в синглтон.

    Returns:
        None
    """
    logger.info("Mining chance calculation started...")
    redis_client = await get_redis()
    users_with_balances = await redis_client.zrange(
        f"users_balances:{settings.REDIS_NODE_TAG_3}", 0, -1, withscores=True
    )
    total_balance = sum(balance for _, balance in users_with_balances)

    mining_chance = round((1 - total_balance / settings.MAX_BLOCKS), 4)
    singleton = get_mining_chance_singleton()
    singleton.set_value(mining_chance)
    logger.info("Mining chance calculated successfully.")
