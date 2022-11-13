from fastapi import APIRouter, Request, Depends, status, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from libs.models import User
from libs.hashing import Hasher
from sqlalchemy.orm import Session
from libs.database import get_db
from configparser import ConfigParser
from jose import jwt
from fastapi.datastructures import URL

config = ConfigParser()
config.read("config/config.ini")


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")
hasher = Hasher()


@router.get("/", include_in_schema=False)
def login_page(response: Response, request: Request, db: Session=Depends(get_db)):
    """
    login page
    """

    errors = []

    token = request.cookies.get("access_token")
    # print(token)
    if not token:
        return templates.TemplateResponse("login.html", {"request": request}) 
    try:
        if token:
            # this part of code is for get token and decode info from token
            scheme,_,param = token.partition(" ")
            payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
            # print(payload) or print(payload['sub'])
            user = db.query(User).filter(User.name==payload['sub']).first()
            if not user:
                return templates.TemplateResponse("login.html", {"request": request})
            if user.is_active == False:
                response.delete_cookie('access_token')
                errors.append('Konto nieaktywne!')
                print("Jak nie działa kurwa???")
                return templates.TemplateResponse("login.html", {'request': request, "errors": errors})
            return RedirectResponse(url="/warehouse")
    except Exception:
        return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", tags=['auth'])
async def login_user(response: Response, request:Request, db:Session=Depends(get_db)):
    """
    login user
    """
    credentials = await request.form()
    username = credentials.get('username')
    password = credentials.get('password')

    errors = []
    try:
        user = db.query(User).filter(User.name==username).first()
        # print(username, password)
        # print(user.name, user.password)
        if user is None:
            errors.append(f"Login lub hasło niepoprawne!")
            return templates.TemplateResponse("login.html", {"request": request, "errors": errors})
        if user.is_active == False:
            errors.append('Konto nieaktywne!')
            print("Jak nie działa kurwa???")
            return templates.TemplateResponse("login.html", {'request': request, "errors": errors})
        if hasher.verify_password(password, user.password):
            data = {"sub": username}
            jwt_token = jwt.encode(
                data, config.get("security", "jwt_secret_key"), algorithm=config.get("security", "algorithm")) # expires variable
            msg = "Login successfully."
            print(msg)
            
            response = RedirectResponse(url="/warehouse")
            response.set_cookie(
                key="access_token", value=f"Bearer {jwt_token}", httponly=True)
            return response
        else: 
            print("Invalid username or password")
            errors.append("Nieprawidłowy login lub hasło!")
            return templates.TemplateResponse("login.html", {"request": request, "errors": errors})
    
    except Exception as e:
        errors.append("Invalid credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details="Invalid credentials")

# test
@router.get("/logout", tags=['auth'])
def logout(response: Response, request: Request):
    """
    logout
    """
    msg = "You logged out successfully."
    response = RedirectResponse(url="/")
    response.delete_cookie(key='access_token')
    # response.set_cookie(key="access_token", value="come-to-the-dark-side-we-have-cookies")
    return response

