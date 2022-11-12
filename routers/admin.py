from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from libs.models import User, Item, InvTable
from libs.hashing import Hasher
from sqlalchemy.orm import Session
from libs.database import get_db
from sqlalchemy.exc import IntegrityError
from configparser import ConfigParser
import libs.tokenizer as Tokenizer


config = ConfigParser()
config.read("config/config.ini")


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")
hasher = Hasher()
tokenizer = Tokenizer.Tokenizer()


@router.get("/admin", tags=['admin'])
def load_admin_panel(request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user_info = tokenizer.check_admin(token, db)
    if not user_info:
        return RedirectResponse("/warehouse")
    
    # print(user_info.name, user_info.is_admin)
    warehouse_value = 0
    items = db.query(Item).all()
    items_count = len(items)

    to_order = 0
    for item in items:
        if item.stack <= item.stack_min:
            to_order += 1
        if item.stack > 0:
            warehouse_value += (item.buy * item.stack)


    active_users = db.query(User).filter(User.is_active==True).all()
    active_users_count = len(active_users)

    inactive_users = db.query(User).filter(User.is_active==False).all()
    inactive_users_count = len(inactive_users)

    inventory = db.query(InvTable).all()
    open_inventory = None
    if inventory:
        open_inventory = "TAK"

    return templates.TemplateResponse("adminpanel.html", {"request": request, "warehouse_value": warehouse_value, "open_inventory": open_inventory, "items_count": items_count, "active_users_count": active_users_count, "inactive_users_count": inactive_users_count, "items_to_order_count": to_order, "user": user_info})


@router.get("/admin/users-events", tags=['admin'])
def load_users_events_page(request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user_info = tokenizer.check_admin(token, db)
    if not user_info:
        return RedirectResponse("/warehouse")

    users = db.query(User).all()
    for _user in users:
        if _user.is_active:
            _user.is_active = "TAK"
        else: _user.is_active = "NIE"
        if _user.is_admin:
            _user.is_admin = "TAK"
        else: _user.is_admin = "NIE"

    return templates.TemplateResponse("/usersevents.html", {"request": request, "user": user_info, "users": users})


@router.get("/admin/users-events/{user_id}", tags=['admin'])
def load_user_event_page(user_id: int, request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user_info = tokenizer.check_admin(token, db)
    if not user_info:
        return RedirectResponse("/warehouse")

    user_event = db.query(User).filter(User.id == user_id).first()
    
    return templates.TemplateResponse("userevent.html", {"request": request, "user": user_info, "user_event": user_event})
