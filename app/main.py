import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from app.config import settings
from app.redis_init import redis_client, init_redis
from app.game_items.router import router as items_router
from app.users.router import router as users_router
from app.improvements.router import router as improvements_router
from app.lots.router import router as lots_router
from app.notifications.router import router as notification_router
from app.pages.router import router as pages_router
from app.clicks.router import router as clicks_router

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
    FastAPICache.init(RedisBackend(redis_client), prefix="cache")
    yield
    logging.info("Service exited")

app = FastAPI(
    title="Proof of Click",
    lifespan=lifespan,
    )

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(users_router)
app.include_router(items_router)
app.include_router(improvements_router)
app.include_router(lots_router)
app.include_router(notification_router)
app.include_router(pages_router)
app.include_router(clicks_router)

origins = settings.ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
