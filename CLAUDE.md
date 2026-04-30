# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access at `http://localhost:8000` (root redirects to `/benefits`). Requires a `.env` file with `GOR_CONNECTION`, `TUG_CONN_STRING`, `SENDGRID_API_KEY`, and email config vars.

## Deployment

Two Windows batch scripts handle deployment to Azure:
- `deploy.bat` — builds and pushes to QA (`gor26-Q` Azure Web App)
- `deploy-prod.bat` — production deployment

Both build a Docker image, push to `gor20206acr.azurecr.io/gorhino-fastapi`, and restart the Azure Web App. The `version.txt` timestamp is injected into all pages via `app/core/templates.py`.

## Architecture Overview

**FastAPI + Jinja2 + HTMX** app serving a dining rewards/benefits portal (GoRhino). No ORM — all DB access is raw SQL via pyodbc against SQL Server, heavy use of stored procedures.

### Entry point

`app/main.py` — mounts 10 routers and serves `/app/static`.

### Routers

| Router | Prefix | Purpose |
|---|---|---|
| `admin.py` | `/admin` | Login, user creation (Argon2 password hashing) |
| `tug.py` | `/benefits` | Benefits/rewards v1 |
| `tug_v2.py` | `/benefits_v2` | Benefits/rewards v2 (active dev) |
| `crm.py` | `/crm` | Customer search and lookup |
| `booking.py` | `/booking` | Booking management |
| `partners.py` | `/partners` | Partner listing and CRUD |
| `partner_admin.py` | `/partner_admin` | Partner admin, image uploads |
| `establishment.py` | `/establishment` | Store/establishment management |
| `landing_v2.py` | `/landing_v2` | Landing page v2 |
| `testing.py` | `/testing` | Email send validation |

### Services

- **`app/services/dal.py`** — all database access. Key functions:
  - `generic_fetch_data(sql, *params)` — returns list of dicts
  - `generic_fetch_multiple_datasets(sql, *params)` — returns `{'result_1': [...], 'result_2': [...]}` for SPs with multiple result sets
  - `generic_execute(sql, *params)` — INSERT/UPDATE with no return
  - `generic_execute_return(sql, *params)` — returns scalar (e.g. new ID)
  - `exec_sp(sp_name, *params)` — stored procedure shorthand
- **`app/services/comms.py`** — SendGrid email (`GenericSendMail`, `send_email_template` for dynamic templates)
- **`app/services/security.py`** — Argon2 password hashing (`hash_pw`, `check_pw`)

### Templates

Located in `app/pages/`, using Jinja2 inheritance from `base.html`. Tailwind CSS loaded from CDN, HTMX 1.9.12 included globally.

### Session / Auth

Cookie-based sessions (no JWT). Login sets httpOnly cookies `customer_id` and `category` with 4-hour expiry. Protected routes check `request.cookies.get("customer_id")` and return a redirect response if missing.

## Key Patterns

**Database calls:**
```python
sql = "exec [spGetCustomerData_2026] ?"
data = dal.generic_fetch_multiple_datasets(sql, customer_id)
customer = data['result_1'][0]
```

**HTMX navigation** — most "page transitions" are 204 responses with an `HX-Redirect` header; the HTMX client handles the redirect:
```python
response = Response(status_code=204)
response.headers["HX-Redirect"] = "/benefits_v2/home"
return response
```

**Template responses:**
```python
from app.core.templates import templates
return templates.TemplateResponse("benefits_v2/home.html", {"request": request, "customer": customer})
```

**File uploads** (partner images) are saved to `/app/static/partners/` with slug-based naming: `{prefix}_cat{category_id}_{slug}{ext}`.

## Standalone Scripts

- `gor_reporting.py` — runs `spFullWeeklyReport`, exports to Excel/CSV, copies to network share. Run via `run_reporting.bat`.
- `sftp_indexer.py` — SFTP operations, not integrated into the main app.

## Two Databases

- **GOR DB** (`GOR_CONNECTION`) — CRM, bookings, admin users
- **TUG DB** (`TUG_CONN_STRING`) — benefits/rewards (partners, categories, customer rewards)

Both are accessed via the same `dal.py` functions; the connection string used depends on which is passed (the dal module reads the correct env var per call).
