# from tokenize import String
# from xmlrpc.client import Boolean
from libs.database import Base
from sqlalchemy import Column, Integer, Boolean, String, Float, Date

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
    
class InvTable(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    reference = Column(String, nullable=False)
    code = Column(String, nullable=False)
    item_id = Column(Integer)
    name = Column(String, nullable=False)
    stack = Column(Integer, nullable=False, default=1)
    added_by = Column(String, nullable=False)
    date = Column(String, nullable=False)