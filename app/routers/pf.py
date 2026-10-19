from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import app.services.dal as DAL
from app.core.templates import templates

router = APIRouter(prefix="/pf")


class PFLoginRequest(BaseModel):
    pf_customer_id: int
    reward_tier: int
    mobile_number: str
    email_address: Optional[str] = None


@router.post("/")
async def pf_login(request: Request, payload: PFLoginRequest):
    context = {"request": request, "customer": payload}
    return templates.TemplateResponse("pf/index.html", context)


@router.get("/simulate")
async def pf_simulate(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("pf/simulate.html", context)


    
