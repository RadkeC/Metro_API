from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Group_Create(BaseModel):
    id: Optional[int]
    name: str
    #created_by: str
    #created_at:str/datetime
    p1: Optional[str]
    p2: Optional[str]
    p3: Optional[str]
    p4: Optional[str]


class Group_Response(Group_Create): # Rozszeża Group_Create
    created_by: str
    created_at: str

    class Config:
        orm_mode = True


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


class Device_Response(Device_Create):
    created_by: str
    created_at: str

    class Config:
        orm_mode = True



