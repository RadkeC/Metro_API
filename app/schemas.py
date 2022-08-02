from fastapi import Form
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Type, NewType
import inspect

StringId = NewType('StringId', str)


# Function to use schemas as HTML form handler
def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


# groups.py -> group_create; group_site.py -> post_group_create, 
@as_form
class Group_Create(BaseModel):
    name: str
    p1: Optional[str]
    p2: Optional[str]
    p3: Optional[str]
    p4: Optional[str]


# groups.py -> group_update
class Group_Update(Group_Create):
    id: int


# groups.py -> group_create, group_get_all, group_get, group_update
class Group_Response(Group_Update): # Rozszeża Group_Update
    created_by: str
    created_at: str

    class Config:
        orm_mode = True


# group_site.py -> post_group_manage
@as_form
class Group_Form(BaseModel):
    name: Optional[str]
    p1: Optional[str]
    p2: Optional[str]
    p3: Optional[str]
    p4: Optional[str]
    id: Optional[int]
    
    
# devices.py -> device_create
@as_form
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


# devices.py -> device_update
class Device_Update(Device_Create):
    id: int


# devices.py -> device_create, device_get_all, device_get, device_update
class Device_Response(Device_Update):
    created_by: str
    created_at: str

    class Config:
        orm_mode = True


# device_site.py -> post_device_create, post_device_manage
@as_form
class Device_Form(BaseModel):
    name: Optional[str]
    model: Optional[str]
    ob: Optional[str]
    localization: Optional[str]
    login: Optional[str]
    password: Optional[str]
    ip: Optional[str]
    mask: Optional[str]
    mac: Optional[str]
    group_name: Optional[str]
    created_by: Optional[str]
    created_at: Optional[str]
    p1: Optional[str]
    p2: Optional[str]
    p3: Optional[str]
    p4: Optional[str]

    on_name: Optional[str]
    on_model: Optional[str]
    on_ob: Optional[str]
    on_localization: Optional[str]
    on_login: Optional[str]
    on_password: Optional[str]
    on_ip: Optional[str]
    on_mask: Optional[str]
    on_mac: Optional[str]
    on_group_name: Optional[str]
    on_created_by: Optional[str]
    on_created_at: Optional[str]
    on_p1: Optional[str]
    on_p2: Optional[str]
    on_p3: Optional[str]
    on_p4: Optional[str]

    exactly_name: Optional[str]
    exactly_model: Optional[str]
    exactly_ob: Optional[str]
    exactly_localization: Optional[str]
    exactly_login: Optional[str]
    exactly_password: Optional[str]
    exactly_ip: Optional[str]
    exactly_mask: Optional[str]
    exactly_mac: Optional[str]
    exactly_group_name: Optional[str]
    exactly_created_by: Optional[str]
    exactly_created_at: Optional[str]
    exactly_p1: Optional[str]
    exactly_p2: Optional[str]
    exactly_p3: Optional[str]
    exactly_p4: Optional[str]
    

# users.py -> user_create
@as_form
class User_Create(BaseModel):
    admin: bool
    name: str
    forename: str
    department: str
    login: str
    password: str


# users.py -> user_update
class User_Update(User_Create):
    id: int


# users.py -> user_create, user_get_all, user_get, user_update
class User_Response(User_Update):
    created_by: str
    created_at: str

    class Config:
        orm_mode = True


@as_form
class User_Form(BaseModel):
    admin: Optional[bool]
    name: Optional[str]
    forename: Optional[str]
    department: Optional[str]
    login: Optional[str]
    password: Optional[str]
    id: Optional[int]


class Token(BaseModel):
    access_token: str
    token_type: str


# oauth2.py -> verify_access_token
class TokenData(BaseModel):
    id: Optional[str] = None


# group_site.py -> post_group_manage; device_site.py -> post_device_create, post_device_manage
@as_form
class Buttons(BaseModel):
    delete_button: Optional[str]
    edit_button: Optional[str]
    accept_button: Optional[str]
    reject_button: Optional[str]
    toggle_button: Optional[str]
    show_button: Optional[str]
    sorting_button: Optional[str]
    generate_button: Optional[str]
    download_raport_button: Optional[str]


# device_site.py -> post_device_manage
@as_form
class Resending_Data(BaseModel):
    selected_groups: str = None
    filters: str = None
    sorting: str = None
    group_checkbox: Optional[str]
    id_form: int = None
    y_offset: str = '0'
    y_offset_div: str = '0'
