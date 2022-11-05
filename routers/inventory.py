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


    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/")
    try:
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except:
        RedirectResponse("/")
    if not user:
        return RedirectResponse("/")
        
    inv_table = db.query(InvTable)
    item_table = []
    for x_item in inv_table:
        item_table.append(
            {
                "id": x_item.id,
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
    
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/")
    try:
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except:
        RedirectResponse("/")
    if not user:
        return RedirectResponse("/")
     
    
    search = await request.form()
    search_item = search.get("searchbar")
    search_by_reference = search.get("searchReference")
    
    if search_by_reference:
        item = db.query(Item).filter(Item.reference==search_item).first()
        print("searching by reference")
        # if item not exist
        error = f"Nie znaleziono towaru o referencji {search_item}!"
    else:
        item = db.query(Item).filter(Item.code==search_item).first()
        print("searching by code")
        # it item not exist
        error = f"Nie znaleziono towaru o kodzie {search_item}!"
        
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
                "id": x_item.id,
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
        
    if item or search_item.replace(' ','')=='':
        return templates.TemplateResponse('/inventory.html', {"request": request, "item_count": item_count, "items": item_table, "username": user.name})
    
    return templates.TemplateResponse('/inventory.html', {"request": request, "item_count": item_count, "items": item_table, "error": error, "username": user.name})


@router.post('/inventory/reset', tags=['inventory'])
def reset_inventory_list(request: Request, db:Session=Depends(get_db)):
    
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/")
    try:
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except:
        RedirectResponse("/")
    if not user:
        return RedirectResponse("/")
     
    
    try:
        db.query(InvTable).delete()
        db.commit()
        return {"response": "success", "msg": "SUKCES!\nPomyślnie wyzerowano listę inwentaryzacji!"}
    except Exception as e:
        return {"response": "error", "msg": f"BŁĄD!\nReset listy nie powiódł się!\nPowód: {str(e)}"}
    

@router.post('/inventory/accept', tags=['inventory'])
def reset_inventory_list(request: Request, db:Session=Depends(get_db)):
    
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/")
    try:
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except:
        RedirectResponse("/")
    if not user:
        return RedirectResponse("/")
     
    
    warehouse_diferences = {}
    inventory_value = 0
    warehouse_value = 0
    
    inventory_stacks = {}
    warehouse_stacks = {}
    warehouse_over_none = {}
    
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
    # print("warehouse stacks: ", warehouse_stacks)
    
    # warehouse_REstack
    # warehouse_diferences
    for comparison in inventory_stacks.keys():
        if comparison in warehouse_stacks.keys():
            _item = db.query(Item).filter(Item.id==comparison).first()
            warehouse_stacks[comparison] -= inventory_stacks[comparison]
            # warehouse_diferences[_item.name] = (_item.buy *- warehouse_stacks[comparison])
            # warehouse_over_none[_item.name] = (_item.stack - warehouse_stacks[comparison])



    for _item in database:
        if _item.id in inventory_stacks.keys():
            _diference = inventory_stacks[_item.id] - _item.stack
            if _diference != 0:
                warehouse_over_none[_item.name]=_diference
            elif _item.stack == inventory_stacks[_item.id]:
                pass
            else:
                warehouse_over_none[_item.name] = inventory_stacks[_item.id]
        else:
            if _item.stack != 0:
                warehouse_over_none[_item.name] = -(_item.stack)
        
            
    
    # warehouse_value
    for row in warehouse_stacks.keys():
        _item = db.query(Item).filter(Item.id==row).first()
        warehouse_value += (_item.buy * _item.stack)
            
    # inventory_value
    for row in inventory_stacks.keys():
        _item = db.query(Item).filter(Item.id==row).first()
        inventory_value += (_item.buy * inventory_stacks[row])
    
    warehouse_financial_state = inventory_value - warehouse_value
    
    # print("inventory stacks: ", inventory_stacks)
    # print("warehouse REstacks: ", warehouse_stacks)
    # print("(+ more / - less) warehouse diferences: ", warehouse_diferences)
    print("inventory value: ", inventory_value)
    print("warehouse value: ", warehouse_value)
    print("warehouse financial state: ", warehouse_financial_state)
    print(f"overstand / none: ", warehouse_over_none)
    
    # database = db.query(Item).all()
    for db_item in database:
        if db_item.id in inventory_stacks.keys():
            # print(db_item.id)
            existing_item = db.query(Item).filter(Item.id==db_item.id)
            existing_item.update({'stack': inventory_stacks[db_item.id]})
        else:
            existing_item = db.query(Item).filter(Item.id==db_item.id)
            existing_item.update({'stack': 0})

    
    db.commit()
    
    db.query(InvTable).delete()
    db.commit()
    
    overstand_none_list = ''
    for poz in warehouse_over_none.keys():
        overstand_none_list += f"{poz}: {warehouse_over_none[poz]} szt.\n"

    overstand_none = f"nadstan / braki:\n\n{overstand_none_list}"

    file_path = f"{config.get('files','inventory')}/inwentaryzacja {time.strftime('%d.%m.%Y')}.txt"

    with open(file_path, "w", encoding=("utf-8")) as inventory_file:
        inventory_file.write(f"Data wykonania: {time.strftime('%d/%m/%Y')}\n\n")
        inventory_file.write(f"{overstand_none}\n\n")
        inventory_file.write(f"Wartość inwentaryzacji:    {inventory_value},-\n")
        inventory_file.write(f"Wartość magazynu przed inwentaryzacją:    {warehouse_value},-\n")
        inventory_file.write(f"Różnica wartości stanu magazynowego:    {warehouse_financial_state},-\n")

    return {
        "response": "success",
        "msg": f"SUKCES!\n\nWYNIK INWENTARYZACJI:\n\n{overstand_none}\n\nWartość inwentaryzacji:    {inventory_value},-\nWartość magazynu przed inwentaryzacją:    {warehouse_value},-\n\nRóżnica wartości stanu magazynowego:    {warehouse_financial_state},-"
        }


@router.delete('/delete_row_from_list/{item_id}', tags=['inventory'])
def delete_row_from_list(item_id: int, request: Request, db: Session=Depends(get_db)):
    
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/")
    try:
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except:
        RedirectResponse("/")
    if not user:
        return RedirectResponse("/")
     

    try:
        db.query(InvTable).filter(InvTable.id==item_id).delete()
        db.commit()
        return {"response": "success", "msg": f"SUKCES!\nPoprawnie usunięto pozycję!"}

    except Exception as e:
        return {"response": "error", "msg": f"Błąd bazy danych:\n{str(e)}"}


