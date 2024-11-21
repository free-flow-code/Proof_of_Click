from fastapi import FastAPI
from slowapi import Limiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from app.config import settings
from app.redis_init import init_redis_cluster
from app.utils.logger_init import logger
from app.utils.rate_limiter import limiter
from app.utils.boosts_init import add_all_boosts_to_redis
from app.utils.mining_chance_init import set_mining_chance

from app.utils.game_items_init import (
    create_game_items,
    set_items_quantity_in_redis
)
from app.utils.users_init import (
    add_top_100_users_to_redis,
    add_all_users_balances_to_redis,
    add_users_with_autoclicker_to_redis
)
from app.lots.router import router as lots_router
from app.users.router import router as users_router
from app.clicks.router import router as clicks_router
from app.game_items.router import router as items_router
from app.boosts.router import router as improvements_router
from app.notifications.router import router as notification_router
from app.general_app_data.router import router as general_app_data_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("The application is launched...")
    global redis_client
    redis_client = await init_redis_cluster()
    await create_game_items()

    if settings.START_INIT_FUNCS:
        await add_all_boosts_to_redis()
        await set_items_quantity_in_redis()
        await add_all_users_balances_to_redis()
        await add_top_100_users_to_redis()
        await add_users_with_autoclicker_to_redis()

    await set_mining_chance()
    FastAPICache.init(RedisBackend(redis_client), prefix="cache")
    logger.info("The application has been launched.")
    yield
    logger.info("Service exited")

app = FastAPI(
    title="Proof of Click",
    lifespan=lifespan,
    )
app.state.limiter: Limiter = limiter  # type: ignore

app.include_router(users_router)
app.include_router(items_router)
app.include_router(improvements_router)
app.include_router(lots_router)
app.include_router(notification_router)
app.include_router(clicks_router)
app.include_router(general_app_data_router)

origins = settings.ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
