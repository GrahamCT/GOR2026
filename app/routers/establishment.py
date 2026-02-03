from fastapi import APIRouter, Request
from app.core.templates import templates

router = APIRouter(prefix="/establishment", tags=["establishment"])

@router.get("/")
async def dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("establishment/index.html", context)