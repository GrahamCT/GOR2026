from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services import comms
import app.services.dal as DAL


from app.core.templates import templates

router = APIRouter(prefix="/benefits", tags=["benefits"])

PARTNERS = [
        {"id": 1, "name": "Partner A", "logo": "https://via.placeholder.com/80?text=A"},
        {"id": 2, "name": "Partner B", "logo": "https://via.placeholder.com/80?text=B"},
        {"id": 3, "name": "Partner C", "logo": "https://via.placeholder.com/80?text=C"},
    ]


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
    
    response = Response(status_code=204)
    if customer[0]['status'] !="ACTIVE":
        response.headers["HX-Redirect"] = "/benefits/support"
    else:
        customer_id = customer[0]['client_id']
    
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
    
    query = "exec [tug_GetInstantCustomer_fromID] ?"
    customer = DAL.dal(1,query,(customer_id,),'TUG')

    context = {"request": request, 
               "customer_id": customer_id, 
                "customer": customer[0]}
    return templates.TemplateResponse("benefits/landing.html", context)


@router.get("/partners", response_class=HTMLResponse)
async def partners_partial(request: Request):

    sql = "select id, partner_name, logo_image  from book_Partner order by NEWID()"

    partners = DAL.dal(1,sql,None,'TUG')


    return templates.TemplateResponse(
        "benefits/_partners.html",
        {"request": request, "partners": partners},
    )


@router.get("/partner/{partner_id}", response_class=HTMLResponse)
async def partner_detail_partial(request: Request, partner_id: int):
    # Returns ONLY the detail "view" partial for selected partner

    sql = "select * from book_Partner where id = ?"

    partner = DAL.dal(1,sql,(partner_id,),'TUG')
    if not partner:
        # Keep it simple for scaffold
        return HTMLResponse("<div>Partner not found</div>", status_code=404)

    customer_id = request.cookies.get("customer_id")

    if customer_id:
        query = 'select id, first_name, last_name, email_address, mobile_number from customer where id = ?'
        customer = DAL.dal(1,query,(customer_id,),'TUG')



    return templates.TemplateResponse(
        "benefits/_partner_detail.html",
        {"request": request, "partner": partner[0], "customer":customer[0]},
    )


@router.post("/request_voucher")
async def request_voucher(request:Request,
                            name: str = Form(...),
                            email: str = Form(...),
                            phone: str = Form(...),
                            partner_id: int = Form(...),
                            customer_id: int = Form(...)
                          ):

    #get a voucher no, asssign it to user, hide the form
    # return voucher number     

    sql = "exec tug_AssignVoucher ?,?"  #partner_id, cust_id

    voucher = DAL.dal(2,sql,(partner_id, customer_id), 'TUG')
    partner = DAL.dal(1,"select * from book_partner where id =?",(partner_id,),'TUG')
    customer= DAL.dal(1,"select * from customer where id = ?",(customer_id,), 'TUG')

       
    
    context = {"request": request, 
               "voucher_number":voucher[0], 
               "partner":partner[0],
               "customer":customer[0]
               }
    
    template_data = {
        "first_name": customer[0]['first_name'],
        "last_name": customer[0]['last_name'],
        "voucher": voucher[0],
        "partner": partner[0]['partner_name']
               }

    subject = f"Your {partner[0]['partner_name']} voucher"

    comms.send_email_template('grahamr@ct-international.co.za',subject,template_data, "d-cf770a728cf04053bddf62d23bde823d"  )
   
    return templates.TemplateResponse("benefits/_booking_voucher.html", context)


@router.get("/support")
async def support(request:Request):
    context = {"request": request}
    return templates.TemplateResponse("benefits/support.html", context)


@router.get("/partner/{partner_id}/detail")
async def get_partner(request:Request):
    context = {"request": request}
    return templates.TemplateResponse("benefits/support.html", context)

