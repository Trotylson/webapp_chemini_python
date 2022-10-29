from tokenize import String
from xmlrpc.client import Boolean
from libs.database import Base
from sqlalchemy import Column, Integer, Boolean, String, Float

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True)
    manufacturer = Column(String)
    reference = Column(String, unique=True, index=True)
    code = Column(String, unique=True, index=True)
    description = Column(String)
    stack = Column(Integer, default=0)
    stack_min = Column(Integer, default=0)
    buy = Column(Float)
    sell = Column(Float)
    used = Column(Boolean, default=False)