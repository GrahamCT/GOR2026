from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse
from app.core.templates import templates

from app.services import security as security
from app.services import dal as dal


router = APIRouter(tags=["admin"], prefix="/login")

@router.get("/")
async def login(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("auth/login.html", context)

@router.get("/admin")
async def admin_dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("admin/dashboard.html", context)  

@router.post("/users")
def create_user(username: str, email_address: str, password: str):
     pw_hash = security.hash_pw(password)
     sql = """
        INSERT INTO dbo.[user] (username, email_address, password_hash)
        VALUES (?, ?, ?)
        """
     
     dal.generic_execute(sql, (username, email_address, pw_hash))
     return {"status": "user created"}  

@router.post("/login_user")
def login_user(username: str = Form(...), password: str = Form(...)):

    sql = """
        SELECT password_hash FROM dbo.[user]
        WHERE username = ?
        """
    result = dal.generic_fetch_data(sql, (username,))
    if result == {"status": "ok"}:
       return HTMLResponse(
            """
            <div id="login-error" class="text-red-500 text-sm">
              Invalid Username or Password
            </div>
            """,
            status_code=200
        )
    
    pw_hash = result[0]['password_hash']
    if security.check_pw(password, pw_hash):
        response=Response()
        response.headers["HX-Redirect"] = "/crm"
        return response
    
    else:
         return HTMLResponse(
            """
            <div id="login-error" class="text-red-500 text-sm">
              Invalid Username or Password
            </div>
            """,
            status_code=200
        )  
