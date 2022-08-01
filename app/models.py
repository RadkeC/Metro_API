from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


# Models of db tables
class Group(Base):
    __tablename__ = 'grupa'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    created_by = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    p1 = Column(String, nullable=True)
    p2 = Column(String, nullable=True)
    p3 = Column(String, nullable=True)
    p4 = Column(String, nullable=True)


class Device(Base):
    __tablename__ = 'urzadzenie'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    model = Column(String, nullable=False)
    ob = Column(String, nullable=False)
    localization = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    ip = Column(String, nullable=False, unique=True)
    mask = Column(String, nullable=False)
    mac = Column(String, nullable=False, unique=True)
    created_by = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    group_name = Column(String, nullable=False)
    p1 = Column(String, nullable=True)
    p2 = Column(String, nullable=True)
    p3 = Column(String, nullable=True)
    p4 = Column(String, nullable=True)


class User(Base):
    __tablename__ = 'uzytkownik'

    id = Column(Integer, primary_key=True, nullable=False)
    admin = Column(Boolean, nullable=False)
    name = Column(String, nullable=False)
    forename = Column(String, nullable=False)
    department = Column(String, nullable=False)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    #created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
