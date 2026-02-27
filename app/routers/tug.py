from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import app.services.dal as DAL


from app.core.templates import templates

router = APIRouter(prefix="/benefits", tags=["benefits"])


@router.get("/")
async def beneifts(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("benefits/index.html", context)

@router.post("/tug_login", response_class=HTMLResponse)
async def tug_login(request: Request, mobile_number: str = Form(...), email_address: str = Form("0")):
    # do lookup / validation here...
    # return a small HTML partial that HTMX will inject into #login-result
    #'0727263407' cancel
    #'0726729147' active

    customer = DAL.dal(1,"exec tug_GetInstantCustomer ?",(mobile_number,),'TUG')

    if customer is None:
        return f"""
        <div class="text-sm text-orange-700 font-semibold">
        Could not find mobile number number: <span class="font-semibold">{mobile_number}</span>
        <span> Please use correct number or contact support on </span>
        
        </div>
        """
    
    customer_id = customer[0]['client_id']

    response = Response(status_code=204)
    
    response.set_cookie(
        key="customer_id",
        value = customer_id,
        httponly=True,      # JS cannot read it
        secure=False,       # True in production (HTTPS)
        samesite="lax",     # Good default
        max_age=60 * 60 * 4 # 4 hours
    ) 
    
    
    response.headers["HX-Redirect"] = "/benefits/landing"
    return response


@router.get("/landing")
async def landing(request: Request):

    customer_id = request.cookies.get("customer_id")
    if not customer_id:
        return RedirectResponse("/benefits")
    


    query = "select id, customer_number, first_name, last_name, email_address, mobile_number from customer where id = ?"

    customer = DAL.dal(1,query,(customer_id,),'TUG')


    
    context = {"request": request, "customer_id": customer_id, "customer": customer[0]}
    return templates.TemplateResponse("benefits/landing.html", context)