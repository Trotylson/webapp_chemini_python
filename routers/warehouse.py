from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from libs.models import User, Item
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


router = APIRouter(include_in_schema=False  )
templates = Jinja2Templates(directory="templates")
hasher = Hasher()



@router.get('/warehouse', tags=['warehouse'])
def call_warehouse_template(request: Request, db:Session=Depends(get_db)):
    """
    Call warehouse page
    """
    errors = []
    try:
        token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
        if not token:
            errors.append("You have to login first.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        # this part of code is for get token and decode info from token
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        # print(payload) or print(payload['sub'])
        user = db.query(User).filter(User.name==payload['sub']).first()
        if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        # end of part
        
        items = db.query(Item).all()
        items_list = []
        for item in items:
            if item.used == True:
                item.used="Tak"
            else: item.used="Nie"
            items_list.append(item)

        return templates.TemplateResponse(
            "warehouse.html",{"request":request, "items": items_list, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})
    except Exception:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})


@router.post('/warehouse', tags=['warehouse'])
async def search_item(request: Request, db:Session=Depends(get_db)):
    """
    POST for item search
    """
    search = await request.form()
    search_item = search.get("searchbar")
    search_used = search.get("searchUsed")
    search_reference = search.get("searchReference")
        
    errors = []

    token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    try:
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except Exception:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    if not user:
        errors.append("User not found.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    try:
        if search_used:
            items = db.query(Item).where((Item.used==True) &
               ((Item.name.like(f"%{search_item}%")) | (Item.reference.like(f"%{search_item}%")) | (Item.code.like(f"%{search_item}%")) | (Item.manufacturer.like(f"%{search_item}%"))))
        elif search_reference:
            items = db.query(Item).where(Item.reference==search_item)
        else:
            items = db.query(Item).where(
            (Item.name.like(f"%{search_item}%")) | (Item.reference.like(f"%{search_item}%")) | (Item.code.like(f"%{search_item}%")) | (Item.manufacturer.like(f"%{search_item}%")))

    except Exception:
        errors.append("Problem z bazą danych.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    if not search_item:
        if search_used:
            items =  db.query(Item).where(Item.used==True)
        else:
            items = db.query(Item).all()
        
    items_list = []
    for item in items:
        if item.used:
            item.used="Tak"
        else: item.used="Nie"
        items_list.append(item)
    
    if search_item==None:
        search_item=''
    
    if len(items_list) == 1:
        # items_list[0].description = items_list[0].description.replace("_g_nl_", "\n")
        reg_description = items_list[0].description.replace("_g_nl_", "\n")
        # print(items_list[0].description)
        return templates.TemplateResponse(
            "warehouse.html",{"request": request, "reg_description":reg_description, "search_item": search_item, "items": items_list, "target":items_list, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})
    return templates.TemplateResponse(
        "warehouse.html",{"request":request, "search_item": search_item, "items": items_list, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})



@router.get('/additem', tags=['warehouse'])
def call_additem_template(request: Request, db:Session=Depends(get_db)):
    """
    Call additem page
    """
    errors = []
    try:
        token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
        if not token:
            errors.append("You have to login first.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        # this part of code is for get token and decode info from token
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        # print(payload) or print(payload['sub'])
        user = db.query(User).filter(User.name==payload['sub']).first()
        if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        # end of part
        return templates.TemplateResponse(
            "additem.html",{"request":request, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})
    except Exception:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})


@router.get('/demand', tags=['warehouse'])
def get_page_with_demand(request: Request, db:Session=Depends(get_db)):
    """
    Call additem page
    """
    errors = []
    try:
        token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
        if not token:
            errors.append("You have to login first.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
        if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        
        # items = db.query(Item).where(Item.stack<=Item.stack_min)
        items_new = db.query(Item).where((Item.used==False) & (Item.stack<=Item.stack_min))
        items_used = db.query(Item).where((Item.used==True) & (Item.stack<=Item.stack_min))
        try:
            
            column_names = ["id", "nazwa", "referencja", "producent", "kod", "stan", "stan min.", "zakup"]
            df = []
            for item in items_new:
                line = [item.id, item.name, item.reference, item.manufacturer, item.code, item.stack, item.stack_min, item.buy]
                df.append(line)
            # demands_new_list = tabulate(df, headers=column_names)
            demands_new_list = tabulate(df, headers=column_names, tablefmt="fancy_grid")
            
            df = []
            for item in items_used:
                line = [item.id, item.name, item.reference, item.manufacturer, item.code, item.stack, item.stack_min, item.buy]
                df.append(line)
            # demands_used_list = tabulate(df, headers=column_names)
            demands_used_list = tabulate(df, headers=column_names, tablefmt="fancy_grid")
            
            with open(f"{config.get('files', 'demands')}/zapotrzebowanie.txt", "w", encoding="utf-8") as demands:
                demands = open(f"{config.get('files', 'demands')}/zapotrzebowanie.txt", "w", encoding="utf-8")
                demands.write(time.strftime("ZAPOTRZEBOWANIE MAGAZYNOWE NA DZIEŃ:   %Y/%M/%d %H:%M:%S\n\n"))
                demands.write("CZĘŚCI NOWE\n")
                demands.write(demands_new_list)
                demands.write("\n\nCZĘŚCI UŻYWANE\n")
                demands.write(demands_used_list)
                demands.write("\n\n")

            # demands = open(f"{config.get('files', 'demands')}/zapotrzebowanie.txt", "w", encoding="utf-8")
            # demands.write(time.strftime("ZAPOTRZEBOWANIE MAGAZYNOWE NA DZIEŃ:   %Y/%M/%d %H:%M:%S\n\n"))
            # demands.write("CZĘŚCI NOWE\n")
            # demands.write(demands_new_list)
            # demands.write("\n\nCZĘŚCI UŻYWANE\n")
            # demands.write(demands_used_list)
            # demands.close()
        except Exception as e:
            print(e)
        
        return templates.TemplateResponse(
            "demand.html",{"request":request, "used_items": items_used, "new_items": items_new, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})
    except Exception:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})


@router.put("/warehouse/item-update-stack", tags = ['warehouse'])
async def edit_item_stack(request: Request, db:Session=Depends(get_db)):
    """
    API edit item stack ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """
    packet = await request.json()
    _id = packet['item_id']
    _quantity = packet['quantity']

    errors = []

    token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})

    existing_item = db.query(Item).filter(Item.id==_id)
    _stack = existing_item.first()
    db_stack = _stack.stack
        
    if db_stack:
        param_stack = db_stack + int(_quantity)
    else: param_stack = _quantity

    payload = {
        "stack":param_stack
    }

    if int(db_stack)+int(_quantity) >= 0:
        try:
            existing_item.update(payload)
            db.commit()
            return {"response": "success", "msg": f"POLECENIE WYKONANE POMYŚLNIE!\n\nRuch towaru: {_quantity}"}
        except IntegrityError as e:
            print(e)
            return {"response": "error", "response": f"Database response: {str(e)}"}
    else:
        return {"response": "error", "msg": "BŁĄD ILOŚCI!\nNie można zdjąć ze stanu więcej towaru niż jest na magazynie!"}
        


@router.put('/warehouse/item-update-all', tags=['warehouse'])
async def update_item_params(request: Request, db:Session=Depends(get_db)):
    """
    API edit item params ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """

    errors = []

    token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})

    packet = await request.json()
    _id = packet['item_id']
    _name = packet['item_name']
    _manufacturer = packet['manufacturer']
    _reference = packet['reference']
    _stack_min = packet['stack_min']
    _buy = packet['buy']
    _sell = packet['sell']
    _description = packet['description']
    _code = packet['code']
    _used = packet['used']
    

    parameters = {"nazwa": _name, "producent": _manufacturer, "referencja": _reference, "stan minimalny": _stack_min, "zakup": _buy, "cena": _sell, "kod": _code}
    for param in parameters:
        if str(parameters[param]).replace(" ","") == "" or parameters[param] == None:
            return {
                "response": "error", "msg": f"PUSTE POLE TOWARU!\nPole {param.upper()} nie może być puste!"} 
    
    if int(_stack_min) < 0:
        return {"response": "error",
                "msg": "BŁĄD ILOŚCI STANU MINIMALNEGO!\nStan minimalny nie może być mniejszy od 0!"}
    
    _stack_min = str(_stack_min).replace(",", ".")
    _sell = str(_sell).replace(",", ".")
    _buy = str(_buy).replace(",", ".")

    existing_item = db.query(Item).filter(Item.id==_id)
    _item = existing_item.first()
    
    # print(_item.name)
    payload = {
        # "stack":_item.stack,
        "name": _name.lower(),
        "manufacturer": _manufacturer.lower(),
        "reference": _reference,
        "code": _code,
        "description": _description,
        "stack_min": _stack_min,
        "buy": _buy,
        "sell": _sell,
        "used": _used
    }

    try:
        existing_item.update(payload)
        db.commit()
        payload['description'] = str(payload['description']).replace("_g_nl_", "\n")
        return {
            "response": "success",
            "msg": f"""SUKCES!\n\nZmiany dla towaru {_name} zostały wprowadzone!\n\n
            NAZWA: {payload['name']}\n
            PRODUCENT: {payload['manufacturer']}\n
            REFERENCJA: {payload['reference']}\n
            KOD: {payload['code']}\n
            STAN MIN.: {payload['stack_min']}\n
            ZAKUP: {payload['buy']}\n
            SPRZEDAŻ: {payload['sell']}\n
            UŻYWANE: {payload['used']}\n
            OPIS: \n{payload['description']}\n"""}
    except IntegrityError as e:
        print(e.__dict__['orig'])
        return {"response": "error", "msg": f"PROBLEM Z EDYCJĄ KARTOTEKI!\nNazwa, referencja i kod to unikatowe wpisy i nie mogą się powtarzać.\nPrawdopodobnie podjęto próbę powielenia któregoś z nich!\nOdpowiedź bazy danych: {e.__dict__['orig']}"}


@router.delete('/warehouse/item-delete-row', tags=['warehouse'])
async def delete_item_row(request: Request, db:Session=Depends(get_db)):
    """
    API delete item row ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """
    packet = await request.json()
    _id = packet['item_id']

    errors = []

    token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})

    item_to_delete = db.query(Item).filter(Item.id==_id)
    
    try:
        item_to_delete.delete()
        db.commit()
        return {
            "response": "success", "msg": f"SUKCES!\n\nPoprawnie usunięto kartotekę towaru o id {_id}."}
    except IntegrityError as e:
        print(e)
        return {"response": "error", "msg": f"Database response: {str(e)}"}


@router.put('/warehouse/additem', tags=['warehouse'])
async def add_item(request: Request, db:Session=Depends(get_db)):
    """
    API PUT new item
    """

    errors = []

    token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
    if not token:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
    scheme,_,param = token.partition(" ")
    payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
    if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})

    packet = await request.json()
    _name = packet['item_name']
    _manufacturer = packet['manufacturer']
    _reference = packet['reference']
    _stack_min = packet['stack_min']
    _buy = packet['buy']
    _sell = packet['sell']
    _description = packet['description']
    _code = packet['code']
    _used = packet['used']
    
    parameters = {"nazwa": _name, "producent": _manufacturer, "referencja": _reference, "stan minimalny": _stack_min, "zakup": _buy, "cena": _sell, "kod": _code}
    for param in parameters:
        if str(parameters[param]).replace(" ","") == "" or parameters[param] == None:
            return {
                "response": "error", "msg": f"PUSTE POLE TOWARU!\nPole {param.upper()} nie może być puste!"} 
    
    name_ex = db.query(Item).filter((Item.name==_name) | (Item.reference==_name) | (Item.code==_name)).first()
    if name_ex:
        return {
            "response": "error", "msg": f"ISTNIEJĄCA NAZWA, REFERENCJA LUB KOD!\nPodana nazwa {_name.upper()} istnieje już jako nazwa, referencja lub kod innego produktu!"}
    reference_ex = db.query(Item).filter((Item.name==_reference) | (Item.reference==_reference) | (Item.code==_reference)).first()
    if reference_ex:
        return {
            "response": "error", "msg": f"ISTNIEJĄCA NAZWA, REFERENCJA LUB KOD!\nPodana referencja {_reference} istnieje już jako nazwa, referencja lub kod innego produktu!"}
    code_ex = db.query(Item).filter((Item.name==_code) | (Item.reference==_code) | (Item.code==_code)).first()
    if code_ex:
        return {
            "response": "error", "msg": f"ISTNIEJĄCA NAZWA, REFERENCJA LUB KOD!\nPodany kod {_code} istnieje już jako nazwa, referencja lub kod innego produktu!"}
    
    
    _stack_min = str(_stack_min).replace(",", ".")
    _sell = str(_sell).replace(",", ".")
    _buy = str(_buy).replace(",", ".")
    
    try:
        new_item = Item(name=_name,manufacturer=_manufacturer, reference=_reference, stack_min=float(_stack_min),
                    buy=float(_buy), sell=float(_sell), description=_description, code=_code, used=_used)
    except ValueError:
        return {
            "response": "error", "msg": "BŁĄD WALIDACJI WARTOŚCI LICZBOWEJ!\nW polu dla wartości liczbowej (stan minimalny, zakup, cena) nie może pojawić się słowo!(stan minimalny, zakup, cena)"}
    except Exception as e:
        return {"response": "error", "msg": f"{str(e)}"}
        
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {
            "response": "success", "msg": f"SUKCES!\n\nPoprawnie dodano kartotekę {_name} o nr referencyjnym {_reference}"}
    except Exception as e:
        return {"response": "error", "msg": f"PROBLEM Z DODANIEM KARTOTEKI dla {_name}!\nOdpowiedź bazy danych:\n\n{str(e)}"}


