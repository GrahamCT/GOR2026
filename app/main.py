from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers import testing
from app.routers import crm 
from app.routers import booking
from app.routers import establishment
from app.routers import admin
from app.routers import tug
from app.routers import partners
from app.routers import partner_admin


app = FastAPI(title="GoRhino")

@app.get("/")
async def root():
    return RedirectResponse(url="/login/")

#ROUTERS
app.include_router(testing.router)
app.include_router(crm.router)
app.include_router(booking.router)
app.include_router(establishment.router)
app.include_router(admin.router)
app.include_router(tug.router)
app.include_router(partners.router)
app.include_router(partner_admin.router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)