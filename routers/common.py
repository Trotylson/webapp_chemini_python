from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Request


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")
templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/funny", include_in_schema=False)
def root(request: Request):
    return templates.TemplateResponse("funny.html", {"request":request})


@router.get("/home")
def home(request: Request):
    """
    home page
    """
    return templates.TemplateResponse("home.html", {"request": request})
