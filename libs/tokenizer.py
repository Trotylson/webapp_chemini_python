from jose import jwt
from configparser import ConfigParser
from libs.models import User


config = ConfigParser()
config.read("config/config.ini")


class Tokenizer():
    def __init__(self):
        pass

    def check_admin(self, token, db):
        if not token:
            return False
        try:
            scheme,_,param = token.partition(" ")
            payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
            user = db.query(User).filter(User.name==payload['sub']).first()
            if not user:
                return False
            if user.is_admin == False:
                return False
            return user
        except Exception:
            return False
        
    def check_user(self, token, db):
        if not token:
            return False
        try:
            scheme,_,param = token.partition(" ")
            payload = jwt.decode(param, config.get("security", "jwt_secret_key"), config.get("security", "algorithm"))
            user = db.query(User).filter(User.name==payload['sub']).first()
            if not user:
                return False
            if user.is_active == False:
                return False
            return user
        except Exception:
            return False