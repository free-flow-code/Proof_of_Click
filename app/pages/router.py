from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.game_items.router import get_user_items

router = APIRouter(
    prefix="/pages",
    tags=["Frontend"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/items")
async def find_hotels_page(
        request: Request,
        items=Depends(get_user_items)
):
    return templates.TemplateResponse(
        name="items.html",
        context={"request": request, "items": items},
    )
