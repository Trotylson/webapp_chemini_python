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


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")
hasher = Hasher()


@router.get('/inventory', tags=['inventory'])
def inventory_template(request: Request, db:Session=Depends(get_db)):

    errors = []

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
    return templates.TemplateResponse("inventory.html", {"request": request, "username": user.name})
