import os
import re
import shutil

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse

from app.core.templates import templates
from app.services.dal import generic_execute, generic_fetch_data

router = APIRouter(prefix="/partner_admin", tags=["partner_admin"])

PARTNERS_QUERY = """
    SELECT p.id, p.partner_name, c.cateogory, p.isActive
    FROM book_Partner p
    JOIN book_category c ON p.book_category_id = c.id
"""

CATEGORIES_QUERY = "SELECT id, cateogory FROM book_category ORDER BY cateogory"

STATIC_PARTNERS_DIR = "app/static/partners"


def _slug(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def _save_upload(upload: UploadFile, prefix: str, slug: str) -> str:
    """Save uploaded file and return the DB path string (partners/filename)."""
    ext = os.path.splitext(upload.filename)[1]
    filename = f"{prefix}_{slug}{ext}"
    dest = os.path.join(STATIC_PARTNERS_DIR, filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return f"partners/{filename}"


@router.get("/")
async def partner_admin_index(request: Request):
    partners = generic_fetch_data(PARTNERS_QUERY) or []
    context = {"request": request, "partners": partners}
    return templates.TemplateResponse("partner_admin/index.html", context)


# ── Add ──────────────────────────────────────────────────────────────────────

@router.get("/add-form", response_class=HTMLResponse)
async def partner_add_form(request: Request):
    categories = generic_fetch_data(CATEGORIES_QUERY) or []
    return templates.TemplateResponse(
        "partner_admin/_add_modal.html",
        {"request": request, "categories": categories},
    )


@router.post("/save", response_class=HTMLResponse)
async def partner_save(
    request: Request,
    partner_name: str = Form(...),
    book_category_id: int = Form(...),
    partner_write_up: str = Form(""),
    partner_offer: str = Form(""),
    logo_image: UploadFile = File(None),
    landing_image: UploadFile = File(None),
):
    slug = _slug(partner_name)

    logo_path = ""
    if logo_image and logo_image.filename:
        logo_path = _save_upload(logo_image, "logo", slug)

    landing_path = ""
    if landing_image and landing_image.filename:
        landing_path = _save_upload(landing_image, "landing", slug)

    sql = """
        INSERT INTO book_partner
            (partner_name, logo_image, landing_image, partner_write_up,
             partner_offer, book_category_id, create_date)
        VALUES (?, ?, ?, ?, ?, ?, GETDATE())
    """
    generic_execute(sql, (partner_name, logo_path, landing_path,
                          partner_write_up, partner_offer, book_category_id))

    partners = generic_fetch_data(PARTNERS_QUERY) or []
    response = templates.TemplateResponse(
        "partner_admin/_table_rows.html",
        {"request": request, "partners": partners},
    )
    response.headers["HX-Trigger"] = "closePartnerModal"
    return response


# ── Edit ─────────────────────────────────────────────────────────────────────

@router.get("/{partner_id}/edit-form", response_class=HTMLResponse)
async def partner_edit_form(request: Request, partner_id: int):
    rows = generic_fetch_data(
        "SELECT * FROM book_partner WHERE id = ?", (partner_id,)
    )
    partner = rows[0] if rows else None
    categories = generic_fetch_data(CATEGORIES_QUERY) or []
    return templates.TemplateResponse(
        "partner_admin/_edit_modal.html",
        {"request": request, "partner": partner, "categories": categories},
    )


@router.post("/{partner_id}/update", response_class=HTMLResponse)
async def partner_update(
    request: Request,
    partner_id: int,
    partner_name: str = Form(...),
    book_category_id: int = Form(...),
    partner_write_up: str = Form(""),
    partner_offer: str = Form(""),
    existing_logo: str = Form(""),
    existing_landing: str = Form(""),
    is_active: str = Form("0"),
    logo_image: UploadFile = File(None),
    landing_image: UploadFile = File(None),
):
    slug = _slug(partner_name)

    logo_path = existing_logo
    if logo_image and logo_image.filename:
        logo_path = _save_upload(logo_image, "logo", slug)

    landing_path = existing_landing
    if landing_image and landing_image.filename:
        landing_path = _save_upload(landing_image, "landing", slug)

    sql = """
        UPDATE book_partner
        SET partner_name = ?,
            logo_image = ?,
            landing_image = ?,
            partner_write_up = ?,
            partner_offer = ?,
            book_category_id = ?,
            isActive = ?
        WHERE id = ?
    """
    generic_execute(sql, (partner_name, logo_path, landing_path,
                          partner_write_up, partner_offer,
                          book_category_id, int(is_active == "1"),
                          partner_id))

    partners = generic_fetch_data(PARTNERS_QUERY) or []
    response = templates.TemplateResponse(
        "partner_admin/_table_rows.html",
        {"request": request, "partners": partners},
    )
    response.headers["HX-Trigger"] = "closePartnerModal"
    return response
