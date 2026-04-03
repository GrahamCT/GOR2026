from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse
from app.core.templates import templates
import app.services.dal as DAL

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("/")
async def partners_index(request: Request):
    sql = "SELECT id, partner_name, logo_image FROM book_partner ORDER BY partner_name"
    partners = DAL.dal(1, sql, None, 'TUG') or []
    context = {"request": request, "partners": partners}
    return templates.TemplateResponse("partners/index.html", context)


@router.get("/search", response_class=HTMLResponse)
async def partners_search(request: Request, q: str = Query("")):
    if q:
        sql = "SELECT id, partner_name, logo_image FROM book_partner WHERE partner_name LIKE ? ORDER BY partner_name"
        partners = DAL.dal(1, sql, (f"%{q}%",), 'TUG') or []
    else:
        sql = "SELECT id, partner_name, logo_image FROM book_partner ORDER BY partner_name"
        partners = DAL.dal(1, sql, None, 'TUG') or []
    return templates.TemplateResponse("partners/_grid.html", {"request": request, "partners": partners})


@router.get("/form", response_class=HTMLResponse)
async def partner_form_new(request: Request):
    return templates.TemplateResponse("partners/_modal_form.html", {"request": request, "partner": None})


@router.get("/{partner_id}/form", response_class=HTMLResponse)
async def partner_form_edit(request: Request, partner_id: int):
    sql = "SELECT * FROM book_partner WHERE id = ?"
    rows = DAL.dal(1, sql, (partner_id,), 'TUG')
    partner = rows[0] if rows else None
    return templates.TemplateResponse("partners/_modal_form.html", {"request": request, "partner": partner})


@router.post("/save", response_class=HTMLResponse)
async def partner_save(
    request: Request,
    partner_id: str = Form(""),
    partner_name: str = Form(""),
    logo_image: str = Form(""),
    landing_image: str = Form(""),
    partner_write_up: str = Form(""),
    partner_offer: str = Form(""),
):
    if partner_id:
        sql = """UPDATE book_partner
                 SET partner_name=?, logo_image=?, landing_image=?, partner_write_up=?, partner_offer=?
                 WHERE id=?"""
        DAL.dal(0, sql, (partner_name, logo_image, landing_image, partner_write_up, partner_offer, int(partner_id)), 'TUG')
    else:
        sql = """INSERT INTO book_partner (partner_name, logo_image, landing_image, partner_write_up, partner_offer, create_date)
                 VALUES (?, ?, ?, ?, ?, GETDATE())"""
        DAL.dal(0, sql, (partner_name, logo_image, landing_image, partner_write_up, partner_offer), 'TUG')

    all_sql = "SELECT id, partner_name, logo_image FROM book_partner ORDER BY partner_name"
    partners = DAL.dal(1, all_sql, None, 'TUG') or []
    response = templates.TemplateResponse("partners/_grid.html", {"request": request, "partners": partners})
    response.headers["HX-Trigger"] = "closePartnerModal"
    return response
