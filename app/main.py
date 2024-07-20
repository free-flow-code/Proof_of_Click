import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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
logging.info("Service started")

app = FastAPI()
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
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization"],
)
