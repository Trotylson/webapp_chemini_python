from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from libs.models import User, Item
from libs.hashing import Hasher
from sqlalchemy.orm import Session
from libs.database import get_db
from sqlalchemy.exc import IntegrityError
from configparser import ConfigParser
from jose import jwt


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
    items = db.query(Item).where(
        (Item.name==search_item) | (Item.reference==search_item) | (Item.code==search_item) | (Item.manufacturer==search_item))
    if not search_item:
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
        return templates.TemplateResponse(
            "warehouse.html",{"request": request, "search_item": search_item, "items": items_list, "target":items_list, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})
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

@router.post('/additem', tags=['warehouse'])
async def add_item(request: Request, db:Session=Depends(get_db)):
    """
    Post new item template
    """
    errors = []

    item = await request.form()
    name=item.get("name").upper()
    manufacturer=item.get("manufacturer").upper()
    reference=item.get("reference")
    stack_min=item.get("stack_min")
    buy=item.get("buy")
    sell=item.get("sell")
    description=item.get("description")
    code=item.get("code")
    used=item.get("used")
    
    if used:
        used=True
    
    try:
        token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
        print(token)
        if not token:
            errors.append("You have to login first.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
        if not user:
            errors.append("User not found.")
            return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
        
        new_item = Item(name=name,manufacturer=manufacturer, reference=reference, stack_min=stack_min, buy=buy, sell=sell, description=description, code=code, used=used)
        try:
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            msg = f"Kartoteka dla {name} została utworzona pomyślnie."
            return templates.TemplateResponse("additem.html", {"request": request, "msg": msg})
        except Exception:
            errors.append(
                f"Kartoteka dla {name} nie została utworzona! Prawdopodobne problemy: referencja lub kod towaru istnieje już w bazie, któryś z wpisów nie jest poprawny (np. zastosowanie przy cenie ',' zamiast '.' lub wpisanie tekstu w miejscu gdzie powinny być cyfry (stan minimalny, zakup, cena, kod))")
            # print(errors)
            return templates.TemplateResponse("additem.html", {"request": request, "errors": errors})

        return templates.TemplateResponse(
            "additem.html",{"request":request})
    except Exception:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})