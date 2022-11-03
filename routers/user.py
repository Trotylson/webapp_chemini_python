from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from libs.models import User
from libs.hashing import Hasher
from sqlalchemy.orm import Session
from libs.database import get_db
from sqlalchemy.exc import IntegrityError
from configparser import ConfigParser
from jose import jwt
from routers.login import oauth2_scheme


config = ConfigParser()
config.read("config/config.ini")


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")
hasher = Hasher()



@router.get('/userinfo', tags=['user'])
def user_info(request: Request, db:Session=Depends(get_db)):
    """
    Actual user inforamtion
    """

    token = request.cookies.get("access_token")     # very important line if you want to authenticate user on page
    if not token:
        return RedirectResponse("/")
    try:
        scheme,_,param = token.partition(" ")
        payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except Exception:
        return RedirectResponse("/")
    if not user:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        "userinfo.html",{"request":request, "user": user.name, "active_status": user.is_active, "is_admin": user.is_admin})


@router.get("/register", include_in_schema=False)
def registration(request: Request):
    """
    registration page
    """
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", tags=['user'])
async def register_user(request: Request, db: Session=Depends(get_db)):
    """
    new user register function.
    """
    form = await request.form()
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    confirm_password = form.get("confirmpassword")
    
    errors = []

    if len(password) < 4:
        errors.append("Password must be less than 4 characters")
        print(errors)
    if password != confirm_password:
        errors.append("Retyped password is not the same as password")
    if errors:
        for error in errors:
            print(error)
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})
    user = User(name=username, email=email, password=hasher.hash_password(password))
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        msg = "Account created successfully! You can now login"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    except IntegrityError:
        errors.append("Username or email already exists")
        print(errors)
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})



