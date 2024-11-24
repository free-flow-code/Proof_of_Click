import redis.asyncio as a_redis
from redis.cluster import ClusterNode
import redis.exceptions as r_exc

from app.utils.logger_init import logger
from app.config import settings


async def init_redis_cluster():
    try:
        startup_nodes = [
            ClusterNode(node["host"], int(node["port"]))
            for node in settings.REDIS_NODES
        ]
        redis_client = a_redis.RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            require_full_coverage=False  # Убирает требование о покрытии всех слотов (для тестов)
        )
        cluster_info = await redis_client.cluster_info()
        if cluster_info.get("cluster_state") == "ok":
            logger.info("Redis Cluster connected.")
        else:
            logger.error("Redis Cluster not ready.")
        return redis_client
    except r_exc.RedisClusterException as err:
        logger.error(f"Redis Cluster connection error: {err}")
        return None
    except Exception as err:
        logger.error(f"Unexpected error: {err}")
        return None

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await init_redis_cluster()
    if redis_client is None:
        logger.error("Failed to initialize Redis Cluster.")
        raise ConnectionError("Failed to initialize Redis Cluster.")
    return redis_client
