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
import time
import os


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


@router.post("/admin/users-events/{user_id}/update-data", tags=['admin'])
async def user_update(user_id: int, request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user = tokenizer.check_admin(token, db)
    if not user:
        return RedirectResponse("/warehouse")

    packet = await request.json()
    newEmail = packet.get("new_email")
    newLogin = packet.get("new_login")
    isActive = packet.get("is_active")
    isAdmin = packet.get("is_admin")

    payload = {
        "email": newEmail,
        "name": newLogin,
        "is_active": isActive,
        "is_admin": isAdmin

    }
    user = db.query(User).filter(User.id == user_id)
    user.update(payload)
    db.commit()

    return {"response": "success", "msg": "SUKCES!\nPomyślnie zaktualizowano dane."}


@router.post("/admin/users-events/{user_id}/update-password", tags=['admin'])
async def user_password_update(user_id: int, request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user = tokenizer.check_admin(token, db)
    if not user:
        return RedirectResponse("/warehouse")

    packet = await request.json()
    newPassword = packet.get("new_password")
    
    if not str(newPassword).strip():
        return {"response": "error", "msg": "BŁĄD!\nKonto bez hasła jest niedozwolone."}

    payload = {
        "password": hasher.hash_password(newPassword)
    }
    user = db.query(User).filter(User.id == user_id)
    user.update(payload)
    db.commit()

    return {"response": "success", "msg": "SUKCES!\nPomyślnie zmieniono hasło."}


@router.get("/admin/database", tags=['admin'])
def load_database_template(request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user = tokenizer.check_admin(token, db)
    if not user:
        return RedirectResponse("/warehouse")
    
    databases = os.listdir("./backups/database_backups/")

    _time = time.strftime("%d/%m/%Y")

    return templates.TemplateResponse("database.html", {"request": request, "databases": databases, "time": _time, "user": user})


@router.post("/admin/database/make-backup", tags=['admin'])
def make_backup(request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user = tokenizer.check_admin(token, db)
    if not user:
        return RedirectResponse("/warehouse")

    _time = time.strftime("%d-%m-%Y")

    try:
        with open("./database/main.db", "rb") as database:
            backup = database.read()
        with open(f"./backups/database_backups/{_time}.bin", "wb") as new_db:
            new_db.write(backup)

        return {"response": "success", "msg": "Wykonano kopię zapasową bazy danych z powodzeniem!"}
    except Exception as e:
        return {"response": "error", "msg": f"{str(e)}"}


@router.post("/admin/database/restore/{db_name}", tags=['admin'])
def restore_database(db_name: str, request: Request, db:Session=Depends(get_db)):
    token = request.cookies.get("access_token")
    user = tokenizer.check_admin(token, db)
    if not user:
        return RedirectResponse("/warehouse")

    _time = time.strftime("%H:%M:%S")

    try:
        with open("./database/main.db", "wb") as database:
            database.write(open(f"./backups/database_backups/{db_name}", "rb").read())

        return {"response": "success", "msg": f"{_time}\nZ powodzeniem przywrucono bazę {db_name}!"}
    except Exception as e:
        return {"response": "error", "msg": f"{str(e)}"}
