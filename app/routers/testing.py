from fastapi import APIRouter, Request
from app.core.templates import templates

router = APIRouter(prefix="/testing", tags=["testing"])

@router.get("/")
async def dashboard(request: Request):
    conext = {"request": request}
    return templates.TemplateResponse("testing/index.html", conext)