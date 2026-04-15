import os
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services import comms
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

    customer = DAL.dal(1,"exec tug_GetInstantCustomer ?",(mobile_number,))

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
        response.headers["HX-Redirect"] = "/benefits/category"
    
    return response


@router.get("/select/{category_id}")
async def select_category(category_id: int):
    response = RedirectResponse("/benefits/landing", status_code=302)
    response.set_cookie(
        key="category",
        value=str(category_id),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 4
    )
    return response


@router.get("/landing")
async def landing(request: Request):

    customer_id = request.cookies.get("customer_id")
    if not customer_id:
        return RedirectResponse("/benefits")

    category_id = int(request.cookies.get("category", 0))
    # category_labels = {
    #     1: "2 for 1 Dining",
    #     2: "2 for 1 Coffee",
    #     3: "2 for 1 Experiences",
    # }
    # category = category_labels.get(category_id, "")

    query = "exec [tug_GetInstantCustomer_fromID] ?"
    customer = DAL.dal(1,query,(customer_id,))

    category = DAL.dal(1,"select * from book_category where id =?", (category_id,))
    


    context = {"request": request,
               "customer_id": customer_id,
               "customer": customer[0],
               "category": category[0]}
    return templates.TemplateResponse("benefits/landing.html", context)


@router.get("/category", response_class=HTMLResponse)
async def category(request: Request):

    context = {"request":request}

    return templates.TemplateResponse(
        "benefits/category.html",context
            )



@router.get("/partners", response_class=HTMLResponse)
async def partners_partial(request: Request):

    category_id = int(request.cookies.get("category", 0))

    sql = """
            select p.id, partner_name, logo_image, category_image, category_header
            from book_Partner P 
            join book_category C on p.book_category_id  = c.id
            where book_category_id=?  and isActive=1
            order by NEWID()
          """

    partners = DAL.dal(1,sql,(category_id,))


    return templates.TemplateResponse(
        "benefits/_partners.html",
        {"request": request, "partners": partners},
    )




@router.get("/partner/{partner_id}", response_class=HTMLResponse)
async def partner_detail_partial(request: Request, partner_id: int):
    # Returns ONLY the detail "view" partial for selected partner

    sql = "select * from book_Partner P join book_category C on p.book_category_id = c.id where p.id = ?"

    partner = DAL.dal(1,sql,(partner_id,))
    if not partner:
        # Keep it simple for scaffold
        return HTMLResponse("<div>Partner not found</div>", status_code=404)

    customer_id = request.cookies.get("customer_id")

    if customer_id:
        query = 'select id, first_name, last_name, email_address, mobile_number from customer where id = ?'
        customer = DAL.dal(1,query,(customer_id,))



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

    voucher = DAL.dal(2,sql,(partner_id, customer_id))
    partner = DAL.dal(1,"select * from book_partner where id =?",(partner_id,))
    customer= DAL.dal(1,"select * from customer where id = ?",(customer_id,))

       
    
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

    is_test = os.getenv("IS_TEST", "False") == "True"
    to_email = os.getenv("TEST_EMAIL") if is_test else customer[0]['email_address']
    comms.send_email_template(to_email, subject, template_data, "d-cf770a728cf04053bddf62d23bde823d")
   
    return templates.TemplateResponse("benefits/_booking_voucher.html", context)


@router.get("/support")
async def support(request:Request):
    context = {"request": request}
    return templates.TemplateResponse("benefits/support.html", context)


@router.get("/partner/{partner_id}/detail")
async def get_partner(request:Request):
    context = {"request": request}
    return templates.TemplateResponse("benefits/support.html", context)


@router.post("/manage_booking", response_class=HTMLResponse)
async def manage_booking(
    book_customer_id: int = Form(...),
    book_name: str = Form(...),
    book_email: str = Form(...),
    book_phone: str = Form(...),
    book_branch: str = Form(...),
    book_datetime: str = Form(...),
    book_guests: int = Form(...),
    partner_id: int = Form(...),
    partner_name: str=Form(...)
):
    sql = "insert into book_booking_tug (client_id, partner_id, booking_date, branch, num_guests) values (?,?,?,?,?)"
    DAL.dal(0, sql, (book_customer_id, partner_id, book_datetime, book_branch, book_guests))

    body = f"""
<table width="100%" cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
  <tr>
    <td align="center">
      
      <table width="500" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; padding: 20px; border: 1px solid #e0e0e0;">
        
        <!-- Header -->
        <tr>
          <td style="font-size: 20px; font-weight: bold; padding-bottom: 15px; color: #333333;">
            📅 New Booking Received
          </td>
        </tr>

        <!-- Divider -->
        <tr>
          <td style="border-top: 1px solid #e0e0e0; padding-top: 15px;"></td>
        </tr>

        <!-- Booking Details -->
        <tr>
          <td>
            <table width="100%" cellpadding="8" cellspacing="0" style="font-size: 14px; color: #444;">
              
              <tr>
                <td style="font-weight: bold; width: 40%;">Name:</td>
                <td>{book_name}</td>
              </tr>

              <tr>
                <td style="font-weight: bold;">Mobile:</td>
                <td>{book_phone}</td>
              </tr>

              <tr>
                <td style="font-weight: bold;">Email:</td>
                <td>{book_email}</td>
              </tr>

              <tr>
                <td style="font-weight: bold;">Partner:</td>
                <td>{partner_name}</td>
              </tr>

              <tr>
                <td style="font-weight: bold;">Branch:</td>
                <td>{book_branch}</td>
              </tr>

              <tr>
                <td style="font-weight: bold;">Booking Date:</td>
                <td>{book_datetime}</td>
              </tr>

              <tr>
                <td style="font-weight: bold;">Guests:</td>
                <td>{book_guests}</td>
              </tr>

            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding-top: 20px; font-size: 12px; color: #888888; text-align: center;">
            This booking was submitted via your website.
          </td>
        </tr>

      </table>

    </td>
  </tr>
</table>
        """


    comms.GenericSendMail("grahamrusson@gmail.com","New Booking Recieved",body)



    return f"""
    <div class="mt-8 p-6 bg-green-50 border border-green-300 rounded-2xl max-w-3xl mx-auto text-sm text-green-800 font-semibold">
        Booking received for <span class="font-bold">{book_name}</span> on {book_datetime}
        for {book_guests} guest(s) at {book_branch}.
        We will confirm via {book_email} or {book_phone}.
    </div>
    """

