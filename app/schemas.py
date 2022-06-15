from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Group_Create(BaseModel):
    name: str
    #created_by: str
    #created_at:str/datetime
    p1: Optional[str]
    p2: Optional[str]
    p3: Optional[str]
    p4: Optional[str]


class Group_Update(Group_Create):
    id: int


class Group_Response(Group_Update): # Rozszeża Group_Update
    created_by: str
    created_at: str

    class Config:
        orm_mode = True


# unused, mb to device_get_all to show short information
class Device_Response_Short(BaseModel):
    name: str
    ob: str
    localization: str
    ip: str
    group_name: str


class Device_Create(BaseModel):
    name: str
    model: str
    ob: str
    localization: str
    login: str
    password: str
    ip: str
    mask: str
    mac: str
    group_name: str
    p1: Optional[str]
    p2: Optional[str]
    p3: Optional[str]
    p4: Optional[str]


class Device_Update(Device_Create):
    id: int

class Device_Response(Device_Update):
    created_by: str
    created_at: str

    class Config:
        orm_mode = True


class User_Create(BaseModel):
    admin: bool
    name: str
    forename: str
    department: str
    login: str
    password: str


class User_Update(User_Create):
    id: int


class User_Response(User_Update):
    created_by: str
    created_at:  datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
