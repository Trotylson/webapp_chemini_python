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
    
    errors = []
    
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
    
    print(type(int(_stack.stack_min)))
    
    if db_stack:
        param_stack = db_stack + int(_quantity)
    else: param_stack = _quantity
    print(param_stack)
    payload = {
        "stack":param_stack
    }

    if int(db_stack)+int(_quantity) >= 0:
        try:
            existing_item.update(payload)
            db.commit()
        except IntegrityError as e:
            print(e)
            return {"code": 500, "response": e}
        
        return {"code": 200, "response": "success"}
    else:
        return {"code": 201, "response": "unsuccess"}
        # errors.append("Nie można zdjąć ze stanu więcej towaru niż jest na magazynie!")
        # return templates.TemplateResponse("home.html", {"request": request, "errors": errors})


@router.put('/chemini-api/item-update-all', tags=['item'])
async def update_item_params(request: Request, db:Session=Depends(get_db), token:str=Depends(oauth2_scheme)):
    """
    API edit item params ::
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer token'}
    """
    packet = await request.json()
    _id = packet['item_id']
    _name = packet['item_name']
    _manufacturer = packet['manufacturer']
    _reference = packet['reference']
    _stack_min = packet['stack_min']
    _buy = packet['buy']
    _sell = packet['sell']
    _description = packet['description']
    _code = packet['code']
    _used = packet['used']

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
        "stack":_item.stack,
        "name": _name.lower(),
        "manufacturer": _manufacturer.lower(),
        "reference": _reference,
        "code": _code,
        "description": _description,
        "stack_min": _stack_min,
        "buy": _buy,
        "sell": _sell,
        "used": _used
    }
    
    print(payload)

    try:
        existing_item.update(payload)
        db.commit()
        # db.refresh(Item)
    except IntegrityError as e:
        print(e)
        return {"code": 500, "response": e}

    return {"code": 200, "response": "success"}


@router.delete('/chemini-api/item-delete-row', tags=['item'])
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
        item_to_delete.delete()
        db.commit()
    except IntegrityError as e:
        print(e)
        return {"code": 500, "response": e}

    return {"code": 200, "response": "success"}


@router.put('/chemini-api/additem', tags=['warehouse'])
async def add_item(request: Request, db:Session=Depends(get_db), token:str=Depends(oauth2_scheme)):
    """
    API PUT new item
    """

    packet = await request.json()
    _name = packet['item_name']
    _manufacturer = packet['manufacturer']
    _reference = packet['reference']
    _stack_min = packet['stack_min']
    _buy = packet['buy']
    _sell = packet['sell']
    _description = packet['description']
    _code = packet['code']
    _used = packet['used']
    
    parameters = [_name, _manufacturer, _reference, _stack_min, _buy, _sell, _code]
    for _value in parameters:
        if str(_value).replace(" ","") == "" or _value == None:
            return {
                "response": "error", "msg": "PUSTE POLE TOWARU!\nPola takie jak nazwa, producent, referencja, stan minimalny, zakup, cena, kod nie mogą być puste!"} 
    
    name_ex = db.query(Item).filter((Item.name==_name) | (Item.reference==_name) | (Item.code==_name)).first()
    if name_ex:
        return {
            "response": "error", "msg": f"ISTNIEJĄCA NAZWA, REFERENCJA LUB KOD!\nPodana nazwa {_name.upper()} istnieje już jako nazwa, referencja lub kod innego produktu!"}
    reference_ex = db.query(Item).filter((Item.name==_reference) | (Item.reference==_reference) | (Item.code==_reference)).first()
    if reference_ex:
        return {
            "response": "error", "msg": f"ISTNIEJĄCA NAZWA, REFERENCJA LUB KOD!\nPodana referencja {_reference} istnieje już jako nazwa, referencja lub kod innego produktu!"}
    code_ex = db.query(Item).filter((Item.name==_code) | (Item.reference==_code) | (Item.code==_code)).first()
    if code_ex:
        return {
            "response": "error", "msg": f"ISTNIEJĄCA NAZWA, REFERENCJA LUB KOD!\nPodany kod {_code} istnieje już jako nazwa, referencja lub kod innego produktu!"}
    
    if not token:
        return {"response": "error", "msg": "NO TOKEN!\nNo authorization token!"}
    try:
        payload = jwt.decode(token, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
        user = db.query(User).filter(User.name==payload['sub']).first()
    except Exception as e:
        return {"response": "error", "msg": "INVALID TOKEN!\nInvalid authorization token construction!"}
        
    if not user:
        return {"response": "error", "msg": "USER NOT FOUND!\nBad user in token!"}
    
    _stack_min = str(_stack_min).replace(",", ".")
    _sell = str(_sell).replace(",", ".")
    _buy = str(_buy).replace(",", ".")
    
    try:
        new_item = Item(name=_name,manufacturer=_manufacturer, reference=_reference, stack_min=float(_stack_min),
                    buy=float(_buy), sell=float(_sell), description=_description, code=_code, used=_used)
    except ValueError:
        return {
            "response": "error", "msg": "BŁĄD WALIDACJI WARTOŚCI LICZBOWEJ!\nW polu dla wartości liczbowej (stan minimalny, zakup, cena) nie może pojawić się słowo!(stan minimalny, zakup, cena)"}
    except Exception as e:
        return {"response": "error", "msg": f"{str(e)}"}
        
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {
            "response": "success", "msg": f"SUKCES!\n\nPoprawnie dodano kartotekę {_name} o nr referencyjnym {_reference}"}
    except Exception as e:
        return {"response": "error", "msg": f"PROBLEM Z DODANIEM KARTOTEKI dla {_name}!\nOdpowiedź bazy danych:\n\n{str(e)}"}
