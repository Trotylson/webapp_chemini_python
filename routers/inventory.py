from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from libs.models import User, Item, InvTable
from libs.hashing import Hasher
from sqlalchemy.orm import Session
from libs.database import get_db
from sqlalchemy.exc import IntegrityError
from configparser import ConfigParser
from jose import jwt
from tabulate import tabulate
import time


config = ConfigParser()
config.read("config/config.ini")


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")
hasher = Hasher()


@router.get('/inventory', tags=['inventory'])
def inventory_template(request: Request, db:Session=Depends(get_db)):

    errors = []

    token = request.cookies.get("access_token")
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
        errors.append("User not found.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        
    inv_table = db.query(InvTable)
    item_table = []
    for x_item in inv_table:
        item_table.append(
            {
                "reference": x_item.reference,
                "code": x_item.code,
                "item_id": x_item.item_id,
                "name": x_item.name,
                "stack": x_item.stack,
                "added_by": x_item.added_by,
                "date": x_item.date
            }
        )
    
    item_count = len(item_table)
    item_table.reverse()
    
    return templates.TemplateResponse("inventory.html", {"request": request, "item_count": item_count, "items": item_table, "username": user.name})


@router.post("/inventory", tags=["inventory"])
async def add_to_inventory(request: Request, db:Session=Depends(get_db)):
    
    errors = []

    token = request.cookies.get("access_token")
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
        errors.append("User not found.")
        return RedirectResponse(url="/")
    
    search = await request.form()
    search_item = search.get("searchbar")
    search_by_reference = search.get("searchReference")
    
    if search_by_reference:
        item = db.query(Item).filter(Item.reference==search_item).first()
        print("searching by reference")
        # print(item)
    else:
        item = db.query(Item).filter(Item.code==search_item).first()
        print("searching by code")
        # print(item)
        
    # db.query(InvTable).delete()
    # db.commit()
    
    if item:
        inv_row = InvTable(reference=item.reference, code=item.code, item_id=item.id, name=item.name, added_by=user.name, date=time.strftime("%d-%m-%Y"))
        db.add(inv_row)
        db.commit()
        db.refresh(inv_row)
        
    inv_table = db.query(InvTable)
    item_table = []
    for x_item in inv_table:
        item_table.append(
            {
                "reference": x_item.reference,
                "code": x_item.code,
                "item_id": x_item.item_id,
                "name": x_item.name,
                "stack": x_item.stack,
                "added_by": x_item.added_by,
                "date": x_item.date
            }
        )
    
    item_count = len(item_table)
    item_table.reverse()
    # print(item_table)
        
    if item or item==None:
        return templates.TemplateResponse('/inventory.html', {"request": request, "item_count": item_count, "items": item_table, "username": user.name})
    
    return templates.TemplateResponse('/inventory.html', {"request": request, "item_count": item_count, "items": item_table, "error": f"Nie znaleziono towaru {search_item}!", "username": user.name})


@router.post('/inventory/reset', tags=['inventory'])
def reset_inventory_list(request: Request, db:Session=Depends(get_db)):
    
    errors = []

    token = request.cookies.get("access_token")
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
        errors.append("User not found.")
        return RedirectResponse(url="/")
    
    try:
        db.query(InvTable).delete()
        db.commit()
        return {"response": "success", "msg": "SUKCES!\nPomyślnie wyzerowano listę inwentaryzacji!"}
    except Exception as e:
        return {"response": "error", "msg": f"BŁĄD!\nReset listy nie powiódł się!\nPowód: {str(e)}"}
    

@router.post('/inventory/accept', tags=['inventory'])
def reset_inventory_list(request: Request, db:Session=Depends(get_db)):
    
    errors = []

    token = request.cookies.get("access_token")
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
        errors.append("User not found.")
        return RedirectResponse(url="/")
    
    warehouse_diferences = {}
    inventory_value = 0
    warehouse_value = 0
    
    inventory_stacks = {}
    warehouse_stacks = {}
    
    # inventory_stacks
    inventory_db = db.query(InvTable).all()
    for inv_item in inventory_db:
        try:
            inventory_stacks[inv_item.item_id] += 1
        except:
            inventory_stacks[inv_item.item_id] = 1
    
    for row in inventory_stacks:
        pass
    
    # warehouse_stacks
    database = db.query(Item).all()
    for db_item in database:
        warehouse_stacks[db_item.id] = db_item.stack
    print("warehouse stacks: ", warehouse_stacks)
    
    # warehouse_REstack
    # warehouse_diferences
    for comparison in inventory_stacks.keys():
        if comparison in warehouse_stacks.keys():
            _item = db.query(Item).filter(Item.id==comparison).first()
            warehouse_stacks[comparison] -= inventory_stacks[comparison]
            warehouse_diferences[_item.name] = (_item.buy *- warehouse_stacks[comparison])
            
    
    # warehouse_value
    for row in warehouse_stacks.keys():
        _item = db.query(Item).filter(Item.id==row).first()
        warehouse_value += (_item.buy * _item.stack)
            
    # inventory_value
    for row in inventory_stacks.keys():
        _item = db.query(Item).filter(Item.id==row).first()
        inventory_value += (_item.buy * inventory_stacks[row])
    
    warehouse_financial_state = warehouse_value - inventory_value
    
    print("inventory stacks: ", inventory_stacks)
    print("warehouse REstacks: ", warehouse_stacks)
    print("(+ more / - less) warehouse diferences: ", warehouse_diferences)
    print("inventory value: ", inventory_value)
    print("warehouse value: ", warehouse_value)
    print("warehouse financial state: ", warehouse_financial_state)
    
    for _id in inventory_stacks.keys():
        existing_item = db.query(Item).filter(Item.id==_id)
        existing_item.update({'stack': inventory_stacks[_id]})
    db.commit()
    
    db.query(InvTable).delete()
    db.commit()
    
    return {"response": "success", "msg": "test api udany :)"}
