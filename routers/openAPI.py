from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from libs.models import Item, User
from libs.hashing import Hasher
from sqlalchemy.orm import Session
from libs.database import get_db
from sqlalchemy.exc import IntegrityError
from configparser import ConfigParser
from jose import jwt
from routers.login import oauth2_scheme


config = ConfigParser()
config.read("config/config.ini")


router = APIRouter()
templates = Jinja2Templates(directory="templates")
hasher = Hasher()


@router.get("/chemini-api/userinfo", tags=['user'])
def userinfo(db:Session=Depends(get_db), token:str=Depends(oauth2_scheme)):
    """
    API user inforamtion ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """
    if not token:
        return {"msg": "Unauthorized - no token."}
    payload = jwt.decode(token, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    user = db.query(User).filter(User.name==payload['sub']).first()
        
    if not user:
        return {"msg": "Unauthorized - user not found or bad token."}
    return {"msg": user}


@router.post("/chemini-api/token", tags = ['user'])
async def receive_token(request: Request, db:Session=Depends(get_db)):
    """
    API get user token after authentication ::
        accepting request with json format => 
        payload = {"usernam":"username", "password":"password"} =>
        headers={"Accept": "application/json"}, json=payload)
    """
    info = await request.json()
    # print(info)
    user = db.query(User).filter(User.name==info['username']).first()
    if not user:
        return{"msg": "No username in database"}
    if not Hasher.verify_password(info['password'] ,user.password):
        return{"msg": "Password incorrect"}
    data = {"sub":info["username"]}
    jwt_token = jwt.encode(data, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
    return {"access_token":jwt_token, "token_type": "bearer"}


@router.put("/chemini-api/item-update-stack", tags = ['item'])
async def edit_item_stack(request: Request, db:Session=Depends(get_db), token:str=Depends(oauth2_scheme)):
    """
    API edit item stack ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """
    packet = await request.json()
    _id = packet['item_id']
    _quantity = packet['quantity']
    
    if not token:
        return {"code": 401, "response": "no token"}
    
    try:
        payload = jwt.decode(token, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except Exception as e:
        return {"code": 401, "response": "invalid token"}
        
    if not user:
        return {"code": 401, "response": "no user found"}

    existing_item = db.query(Item).filter(Item.id==_id)
    _stack = existing_item.first()
    db_stack = _stack.stack
    
    if db_stack:
        param_stack = db_stack + int(_quantity)
    else: param_stack = _quantity
    print(param_stack)
    payload = {
        "id": _stack.id,
        "stack":param_stack,
        "name": _stack.name,
        "manufacturer": _stack.manufacturer,
        "reference": _stack.reference,
        "code": _stack.code,
        "description": _stack.description,
        "stack_min": _stack.stack_min,
        "buy": _stack.buy,
        "sell": _stack.sell,
        "used": _stack.used
    }

    try:
        existing_item.update(payload)
    except IntegrityError as e:
        print(e)
        return {"code": 500, "response": e}
    
    return {"code": 200, "response": "success"}


@router.put('/chemini-api/item-update-all', tags=['item'])
async def update_item_params(request: Request, db:Session=Depends(get_db), token:str=Depends(oauth2_scheme)):
    """
    API edit item params ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """
    packet = await request.json()
    _id = packet['item_id']

    if not token:
        return {"code": 401, "response": "no token"}
    try:
        payload = jwt.decode(token, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except Exception as e:
        return {"code": 401, "response": "invalid token"}
        
    if not user:
        return {"code": 401, "response": "no user found"}

    existing_item = db.query(Item).filter(Item.id==_id)
    _item = existing_item.first()
    
    print(_item.name)
    payload = {
        # "id": _item.id,
        "stack":_item.stack,
        "name": _item.name,
        "manufacturer": _item.manufacturer,
        "reference": _item.reference,
        "code": _item.code,
        "description": _item.description,
        "stack_min": _item.stack_min,
        "buy": _item.buy,
        "sell": _item.sell,
        "used": _item.used
    }

    try:
        existing_item.update(payload)
    except IntegrityError as e:
        print(e)
        return {"code": 500, "response": e}

    return {"code": 200, "response": "success"}


@router.post('/chemini-api/item-delete', tags=['item'])
async def delete_item_row(request: Request, db:Session=Depends(get_db), token:str=Depends(oauth2_scheme)):
    """
    API delete item row ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """
    packet = await request.json()
    _id = packet['item_id']

    if not token:
        return {"code": 401, "response": "no token"}
    try:
        payload = jwt.decode(token, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except Exception as e:
        return {"code": 401, "response": "invalid token"}
        
    if not user:
        return {"code": 401, "response": "no user found"}

    item_to_delete = db.query(Item).filter(Item.id==_id)

    try:
        db.delete(item_to_delete)
    except IntegrityError as e:
        print(e)
        return {"code": 500, "response": e}

    return {"code": 200, "response": "success"}
