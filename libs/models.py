# from tokenize import String
# from xmlrpc.client import Boolean
from libs.database import Base
from sqlalchemy import Column, Integer, Boolean, String, Float

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, nullable=False)
    manufacturer = Column(String, nullable=False)
    reference = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, index=True)
    description = Column(String)
    stack = Column(Integer, nullable=False, default=0)
    stack_min = Column(Integer, nullable=False, default=0)
    buy = Column(Float)
    sell = Column(Float)
    used = Column(Boolean, default=False)