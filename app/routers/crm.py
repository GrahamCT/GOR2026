from fastapi import APIRouter, Form, Request
from app.core.templates import templates
import app.services.dal as dal

#TEST: 0842908212 - MULTIPLE 0824697194 - SINGLE



router = APIRouter(prefix="/crm", tags=["crm"])

@router.get("/")
async def dashboard(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("crm/index.html", context)

@router.post("/get_client")
async def get_client( request: Request, search_for:str =Form(...),):

    #SEARCH FOR CUSTOMER, IF NOTHING FOUND, SHOW ICON, IF ONE FOUND SHOW PANELS
    #IF MULTIPLE FOUND THEN SHOW DROP DOWN AND ON DROPDOWN SELECT SHOW PANELS

    #CLEAN THE INCOMING
    normalized = search_for.replace(" ","").replace("-","")

    #do we have a 1, many on no customers. 
    sql = "select * from customer where customer_number= ? or mobile_number = ?"
    rows = dal.generic_fetch_data(sql, (search_for, normalized,))

    if rows is None:
        context = {
           "request": request,
            "search_for": search_for
            }
        return templates.TemplateResponse('crm/_record_not_found.html', context)
    
    if len(rows)==1:
        context = {
         "request": request,
         "search_for": search_for,
         # add client data here
         }

        return templates.TemplateResponse('crm/_card_data.html', context)
    
    if len(rows)>1:
        context = {
         "request": request,
         "search_for": search_for,
         "customers":rows
         # add client data here
         }

        return templates.TemplateResponse('crm/_multiple_found.html', context)







    # s=1
    # context = {
    #     "request": request,
    #     "search_for": search_for,
    #     # add client data here
    # }

    # # return templates.TemplateResponse('crm/_card_data.html', context)

    

    # return templates.TemplateResponse('crm/_multiple_found.html', context)





