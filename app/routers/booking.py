from fastapi import APIRouter, Request
from app.core.templates import templates

router = APIRouter(prefix="/booking", tags=["booking"])

@router.get("/")
async def dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("booking/index.html", context)