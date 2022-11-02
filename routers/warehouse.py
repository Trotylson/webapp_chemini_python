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
            
            demands = open(f"{config.get('files', 'demands')}/zapotrzebowanie.txt", "w", encoding="utf-8")
            demands.write(time.strftime("ZAPOTRZEBOWANIE MAGAZYNOWE NA DZIEŃ:   %Y/%M/%d %H:%M:%S\n\n"))
            demands.write("CZĘŚCI NOWE\n")
            demands.write(demands_new_list)
            demands.write("\n\nCZĘŚCI UŻYWANE\n")
            demands.write(demands_used_list)
            demands.close()
        except Exception as e:
            print(e)
        
        return templates.TemplateResponse(
            "demand.html",{"request":request, "used_items": items_used, "new_items": items_new, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})
    except Exception:
        errors.append("You have to login first.")
        return templates.TemplateResponse("home.html", {"request": request, "errors": errors})
