from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


"""class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")"""


class Group(Base):
    __tablename__ = 'grupa'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    created_by = Column(String, nullable=False) # mb foreign_key to user
    created_at = Column(String, nullable=False)
    #created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
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
    created_by = Column(String, nullable=False)  # mb foreign_key to user
    created_at = Column(String, nullable=False)
    group_name = Column(String, nullable=False)  # mb foreign_key to group
    #created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    p1 = Column(String, nullable=True)
    p2 = Column(String, nullable=True)
    p3 = Column(String, nullable=True)
    p4 = Column(String, nullable=True)


    #group_id = Column(Integer, ForeignKey("grupa.id", ondelete="CASCADE"), nullable=False)
    #group = relationship("Group")


class User(Base):
    __tablename__ = 'urzytkownik'

    id = Column(Integer, primary_key=True, nullable=False)
    admin = Column(Boolean, nullable=False)
    name = Column(String, nullable=False)
    forename = Column(String, nullable=False)
    department = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_by = Column(String, nullable=False)  # mb foreign_key to user
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

