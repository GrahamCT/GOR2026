from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse
from app.core.templates import templates
import app.services.dal as dal

router = APIRouter(prefix="/booking", tags=["booking"])

@router.get("/")
async def dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("booking/index.html", context)


@router.get("/booking_new/{customer_id}")
async def booking_new(request: Request, customer_id: int):

    sql = "exec [spGetCustomerData_2026] ?"
    data  = dal.generic_fetch_multiple_datasets(sql, customer_id)
    customer = data['result_1'][0]
    benefits = data['result_4']

    sql = "select id, group_name  from [dbo].[book_group] order by group_name"
    partners = dal.generic_fetch_data(sql,())
        
    context = {"request": request, "customer" : customer, "benefits":benefits, "partners":partners}
    
    return templates.TemplateResponse("booking/new_booking.html", context)


@router.get("/get_stores", response_class=HTMLResponse)
async def get_stores(partner_id: int = Query(None)):
    if not partner_id:
        return '<option value="">Select store</option>'

    query = """
        SELECT establishment_id, branch
        FROM dbo.book_establishment
        WHERE group_id = ?
        ORDER BY branch
    """

    stores = dal.generic_fetch_data(query, (partner_id,)) or []

    options = ['<option value="">Select store</option>']
    for store in stores:
        options.append(
            f'<option value="{store["establishment_id"]}">{store["branch"]}</option>'
        )

    return "".join(options)

@router.post("/booking_new/{customer_id}", response_class=HTMLResponse)
async def booking_new_post(
    request: Request,
    customer_id: int,
    booking_datetime: str = Form(""),
    partner_id: str = Form(""),
    store_id: str = Form(""),
    origination: str = Form(""),
    benefit_id: str = Form(""),
    booking_details: str = Form(""),
    value_saving_text: str = Form("")
):
    
    sql = "exec spBookingNew ?,?,?,?,?,?,?" #customerid, bookingdate, partner id, deails, value saving, benefit id, orignation
    dal.generic_execute(sql, (customer_id, booking_datetime, partner_id, booking_details, value_saving_text,benefit_id,origination))

    return """
    <div class="rounded-2xl border border-lime-200 bg-lime-50 p-6">
      <h2 class="text-lg font-semibold text-lime-800 mb-2">Booking saved</h2>
      <p class="text-slate-700">The booking was successfully captured.</p>
      <div class="mt-4">
        <a href="/customers" class="inline-block rounded-xl bg-lime-500 px-4 py-2 text-white font-semibold hover:bg-lime-600 transition">
          Back to customers
        </a>
      </div>
    </div>
    """
