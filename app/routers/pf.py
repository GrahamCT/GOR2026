from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
import app.services.dal as DAL
from app.core.templates import templates

router = APIRouter(prefix="/pf")

@router.get("/")
async def pf_login():
    return {"ok": True}
