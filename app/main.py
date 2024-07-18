import logging
from fastapi import FastAPI
from app.game_items.router import router as items_router
from app.users.router import router as users_router

logging.basicConfig(
        level=logging.DEBUG,
        filename='main_log.log',
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s'
    )
logging.info("Service started")

app = FastAPI()

app.include_router(users_router)
app.include_router(items_router)


def main():
    pass


if __name__ == '__main__':
    main()
