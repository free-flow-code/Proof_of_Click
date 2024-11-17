import logging
from fastapi import FastAPI
from slowapi import Limiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from app.config import settings
from app.redis_init import init_redis
from app.utils.rate_limiter import limiter
from app.utils.data_processing_funcs import load_boosts, load_all_users_balances
from app.utils.mining_chance_init import set_mining_chance
from app.utils.game_items_init import create_game_items
from app.game_items.router import router as items_router
from app.users.router import router as users_router
from app.improvements.router import router as improvements_router
from app.lots.router import router as lots_router
from app.notifications.router import router as notification_router
from app.clicks.router import router as clicks_router
from app.general_app_data.router import router as general_app_data_router

logging.basicConfig(
        level=logging.DEBUG,
        filename='main_log.log',
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s'
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Service started")
    global redis_client
    redis_client = await init_redis()
    await load_boosts(redis_client)
    await create_game_items(redis_client)
    await set_mining_chance(redis_client)
    await load_all_users_balances(redis_client)
    FastAPICache.init(RedisBackend(redis_client), prefix="cache")
    yield
    logging.info("Service exited")

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
