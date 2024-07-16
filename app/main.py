from fastapi import FastAPI
from app.game_items.router import router as items_router


app = FastAPI()

app.include_router(items_router)


def main():
    pass


if __name__ == '__main__':
    main()
