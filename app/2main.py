from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import testing
from app.routers import crm 
from app.routers import booking
from app.routers import establishment
from app.routers import admin
from app.routers import tug


app = FastAPI(title="GoRhino")

#ROUTERS
app.include_router(testing.router)
app.include_router(crm.router)
app.include_router(booking.router)
app.include_router(establishment.router)
app.include_router(admin.router)
app.include_router(tug.router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)