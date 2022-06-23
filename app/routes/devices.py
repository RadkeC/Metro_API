from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime


from app.database import get_db
from app.utils import is_admin
from app import schemas, models, oauth2


router = APIRouter(
    prefix="/API",
    tags=['Devices']
)


# Device
@router.post('/device_create', status_code=status.HTTP_201_CREATED, response_model=schemas.Device_Response)
def device_create(device: schemas.Device_Create, db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    is_admin(current_user)
    if db.query(models.Device).filter(models.Device.name == device.name).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with name: "{device.name}" already exists')
    elif db.query(models.Device).filter(models.Device.ip == device.ip).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with ip: "{device.ip}" already exists')
    elif db.query(models.Device).filter(models.Device.mac == device.mac).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with MAC: "{device.mac}" already exists')
    group = db.query(models.Group).filter(models.Group.name == device.group_name).first()
    if not group.name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group: "{group.name}" does not exists')

    """for n, [g, d] in enumerate([[group.p1, device.p1], [group.p2, device.p2], [group.p3, device.p3], [group.p4, device.p4]]):
        if g and not d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Group require additional parameter from device. Add: {g}.')
        elif not g:
            setattr(device, 'p'+str(n+1), None)"""

    for [g, d] in [[group.p1, 'p1'], [group.p2, 'p2'], [group.p3, 'p3'], [group.p4, 'p4']]:
        if g and not getattr(device, d):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Group require additional parameter from device. Add: {g}.')
        elif not g:
            setattr(device, d, None)

    new_device = models.Device(created_by=current_user.login, created_at=str(datetime.now())[0:16], **device.dict())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


@router.get("/device_get_all", status_code=status.HTTP_200_OK, response_model=List[schemas.Device_Response])
def device_get_all(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    devices = db.query(models.Device).order_by(models.Device.group_name).all()
    if not devices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There are not any devices')
    return devices


@router.get("/device_get", status_code=status.HTTP_200_OK, response_model=List[schemas.Device_Response])
def device_get(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
               name: Optional[str] = '', model: Optional[str] = '',  mac: Optional[str] = '',
               ob: Optional[str] = '', localization: Optional[str] = '',
               ip: Optional[str] = '', mask: Optional[str] = '', group_name: Optional[str] = '',
               p1: Optional[str] = '', p2: Optional[str] = '', p3: Optional[str] = '', p4: Optional[str] = '',
               created_by: Optional[str] = '', created_at: Optional[str] = ''):

    params = locals().copy()
    params.pop('db')
    params.pop('current_user')
    devices = db.query(models.Device).order_by(models.Device.group_name)
    for attribute in [x for x in params if params[x] != '']:# '' w defaulcie można zamienić na None
        devices = devices.filter(getattr(models.Device, attribute).like(params[attribute]))
    devices = devices.all()

    if not devices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There are not any devices with specified constraints')
    return devices


@router.delete("/device_delete/{name}", status_code=status.HTTP_200_OK)
def device_delete(name: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    is_admin(current_user)
    device = db.query(models.Device).filter(models.Device.name == name) # mb instead of name: ip, id, mac
    if not device.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device with name: {name} does not exists")
    device.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted device: {name}"


@router.put("/device_update", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Device_Response)
def device_update(device: schemas.Device_Update, db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    is_admin(current_user)
    device_to_update_query = db.query(models.Device).filter(models.Device.id == device.id)
    device_to_update = device_to_update_query.first()
    if not device_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device with id: {device.id} does not exists")

    for p in ['p1', 'p2', 'p3', 'p4']:
        if not getattr(device_to_update, p):
            setattr(device, p, None)

    device = device.dict()
    device['created_by'] = device_to_update.created_by + '\n' + current_user.login
    device['created_at'] = device_to_update.created_at + '\n' + str(datetime.now())[0:16]
    device_to_update_query.update(device, synchronize_session=False)
    db.commit()

    return device_to_update_query.first()