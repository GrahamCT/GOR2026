from fastapi import APIRouter, Request
from app.core.templates import templates

router = APIRouter(prefix="/v2/landing", tags=["landing-v2"])


@router.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing_v2/index.html", {"request": request})
