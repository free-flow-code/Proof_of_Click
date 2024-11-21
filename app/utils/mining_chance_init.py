from app.utils.logger_init import logger
from app.config import settings
from app.redis_init import get_redis
from app.redis_helpers.lua_scripts import total_sum_script


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
    redis_client = await get_redis()
    mining_chance = 1
    key = f"users_balances:{settings.REDIS_NODE_TAG_3}"

    if await redis_client.exists(key):
        logger.info("Mining chance calculation started...")
        script = redis_client.register_script(total_sum_script)
        total_sum = await script(keys=[key])
        mining_chance = round((1 - total_sum / settings.MAX_BLOCKS), 4)

    singleton = get_mining_chance_singleton()
    singleton.set_value(mining_chance)
    logger.info("Mining chance calculated successfully.")
