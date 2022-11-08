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
    
    print(user_info.name, user_info.is_admin)
    return templates.TemplateResponse("adminpanel.html", {"request": request, "user": user_info})
