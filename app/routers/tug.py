from fastapi import APIRouter, Request

from app.core.templates import templates

router = APIRouter(prefix="/benefits", tags=["benefits"])


@router.get("/")
async def beneifts(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("benefits/index.html", context)