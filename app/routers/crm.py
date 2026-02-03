from fastapi import APIRouter, Request
from app.core.templates import templates

router = APIRouter(prefix="/crm", tags=["crm"])

@router.get("/")
async def dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("crm/index.html", context)