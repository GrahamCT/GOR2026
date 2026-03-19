from fastapi import APIRouter, Request
from app.core.templates import templates

import app.services.comms as comms




router = APIRouter(prefix="/testing", tags=["testing"])

@router.get("/")
async def dashboard(request: Request):
    conext = {"request": request}
    return templates.TemplateResponse("testing/index.html", conext)


@router.post("/send-email")
def send_email():
    template_data = {
    "first_name": "Tira",
    "last_name": "Misu",
    "voucher": "9710500218963669",
    "partner": "Spur"
}

    comms.send_email_template('grahamr@ct-international.co.za','Your Spur voucher',template_data, "d-cf770a728cf04053bddf62d23bde823d"  )
    # comms.SendMail('grahamr@ct-international.co.za','subject')

    return {"status": "sent"}
