from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import re

from app import schemas, models, oauth2
from app.config import hash_device_password, unhash_device_password
from app.database import get_db
from app.utils import is_admin


router = APIRouter(
    prefix="/API",
    tags=['Devices']
)


# Device
@router.post('/device_create', status_code=status.HTTP_201_CREATED, response_model=schemas.Device_Response)
def device_create(device: schemas.Device_Create, db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    # Check if user is permissed to do that, if not raise 401 error
    is_admin(current_user)

    # Checking unique name, IP, MAC
    if db.query(models.Device).filter(models.Device.name == device.name).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with name: "{device.name}" already exists')
    elif db.query(models.Device).filter(models.Device.ip == device.ip).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with ip: "{device.ip}" already exists')
    elif db.query(models.Device).filter(models.Device.mac == device.mac).first() and device.mac != 'b.d.':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with MAC: "{device.mac}" already exists')

    # Checking if send group exists
    group = db.query(models.Group).filter(models.Group.name == device.group_name).all()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group: "{device.group_name}" does not exists')
    group = group[0]

    # Checking if device schema match group parameters p1-p4
    for [g, d] in [[group.p1, 'p1'], [group.p2, 'p2'], [group.p3, 'p3'], [group.p4, 'p4']]:
        if g and not getattr(device, d):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Group require additional parameter from device. Add: {g}.')
        # CHanging 'None' from HTML form to None ?
        elif not g:
            setattr(device, d, None)

    # Hashing password -> utils.py
    device.password = hash_device_password(device.password)

    # Adding device to db
    new_device = models.Device(created_by=current_user.login, created_at=str(datetime.now())[0:16], **device.dict())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


@router.get("/device_get_all", status_code=status.HTTP_200_OK, response_model=List[schemas.Device_Response])
def device_get_all(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # SQLAlchemy question for get all devices
    devices = db.query(models.Device).order_by(models.Device.group_name).all()

    if not devices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There are not any devices')

    # Unhashing device's passwords -> config.py
    for device in devices:
        device.password = unhash_device_password(device.password)

    return devices


@router.get("/device_get", status_code=status.HTTP_200_OK, response_model=List[schemas.Device_Response])
def device_get(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
               name: Optional[str] = '', model: Optional[str] = '',  mac: Optional[str] = '',
               ob: Optional[str] = '', localization: Optional[str] = '',
               ip: Optional[str] = '', mask: Optional[str] = '', group_name: Optional[str] = '',
               p1: Optional[str] = '', p2: Optional[str] = '', p3: Optional[str] = '', p4: Optional[str] = '',
               created_by: Optional[str] = '', created_at: Optional[str] = '', sort_by: Optional[str] = '',
               sort_way: Optional[str] = ''):

    # Deleting from incoming dada attributes that aren't part of device schema
    params = locals().copy()
    params.pop('db')
    params.pop('sort_by')
    params.pop('sort_way')
    params.pop('current_user')

    # Creating SQLAlchemy question and adding constraints
    devices = db.query(models.Device)
    for attribute in [x for x in params if params[x] != '']: # '' w defaulcie można zamienić na None
        devices = devices.filter(getattr(models.Device, attribute).like(params[attribute]))

    # Adding sort constaints to SQLAlchemy question
    # if sort_by and sort_way:
    #    if sort_way == 'asc':
    #        devices = devices.order_by(getattr(models.Device, sort_by))
    #    elif sort_way == 'desc':
    #        devices = devices.order_by((getattr(models.Device, sort_by)).desc())

    # Getting devices that match constaints
    devices = devices.all()

    if not devices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There are not any devices with specified constraints')

    # New sorting including alfanumerical sort
    if sort_by and sort_way:
        new_devices = []
        sort_words = []
        lengths = []

        # Creating list of alfababetical and numerical parts ['AB', '12', 'ERT', '34', ' tyu ']
        for device in devices:
            sort_word = re.split(r'(\d+)', device.__getattribute__(sort_by))
            sort_word = list(filter(''.__ne__, sort_word))
            sort_words.append(sort_word)

            # Extending lengths list to length equal the longest sort_word
            while len(sort_word) > len(lengths):
                lengths.append(0)

            # Update lengths list if any part is longer then earlier longest
            for n, part in enumerate(sort_word):
                if len(part) > lengths[n]:
                    lengths[n] = len(part)

        # Adding paces (' ') to sort_words (to numbers on left, to letters on right)
        for i, sort_word in enumerate(sort_words):
            for n, word in enumerate(sort_word):
                try:
                    int(word)
                    while len(word) < lengths[n]:
                        word = ' ' + word
                    sort_words[i][n] = word
                except:
                    while len(word) < lengths[n]:
                        word = word + ' '
                    sort_words[i][n] = word

            # Creating list of dicts to sort by 'sort' key. 'model' contains model.User object
            new_devices.append({'model': devices[i], 'sort': ''.join(sort_words[i])})

        # Sort with direction
        if sort_way == 'asc':
            new_devices = sorted(new_devices, key=lambda k: k['sort'])
        elif sort_way == 'desc':
            new_devices = sorted(new_devices, key=lambda k: k['sort'], reverse=True)

        # Create sorted list to return
        devices = []
        for device in new_devices:
            devices.append(device['model'])

    # Unhashing devices passwords -> config.py
    for device in devices:
        device.password = unhash_device_password(device.password)

    return devices


@router.delete("/device_delete", status_code=status.HTTP_200_OK)
def device_delete(name: str, db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    # Check if user is permissed to do that, if not raise 401 error
    is_admin(current_user)

    # SQLAlchemy question for get device we want delete
    device = db.query(models.Device).filter(models.Device.name == name)

    if not device.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device with name: {name} does not exists")

    # Deleting device from db
    device.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted device: {name}"


@router.delete("/device_delete_all", status_code=status.HTTP_200_OK)
def device_delete_all(group_name: str, db: Session = Depends(get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
    # Check if user is permissed to do that, if not raise 401 error
    is_admin(current_user)

    # SQLAlchemy question for get device we want delete
    device = db.query(models.Device).filter(models.Device.group_name == group_name)

    if not device.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is not any device in: {group_name} group")

    # Deleting device from db
    device.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted all devices in: {group_name} group"


@router.put("/device_update", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Device_Response)
def device_update(device: schemas.Device_Update, db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    # Check if user is permissed to do that, if not raise 401 error
    is_admin(current_user)

    # SQLAlchemy question for get:
    #       device_to_update - device we want update;
    #       device_to_uniques - list of devices to check unique name, ip and mac
    device_to_uniques = db.query(models.Device).all()
    device_to_update_query = db.query(models.Device).filter(models.Device.id == device.id)
    device_to_update = device_to_update_query.first()

    if not device_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device with id: {device.id} does not exists")

    # Create list of uniques variables for all devices
    uniques = [{'name': d.name, 'ip': d.ip, 'mac': d.mac, 'id': d.id}for d in device_to_uniques]

    # Check if we don't change unique variable to used value
    for unique in uniques:
        if (device.name == unique['name'] or device.ip == unique['ip'] or (device.mac == unique['mac'] and
            device.mac != 'b.d.')) and device.id != unique['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Device with name: "{device.name}", ip: {device.ip} or mac: {device.mac} '
                                       f'does already exists')

    # Setting to None unused parameters from input schema bcs group requirements
    for p in ['p1', 'p2', 'p3', 'p4']:
        if not getattr(device_to_update, p):
            setattr(device, p, None)

    # Hashing device password -> config.py
    device.password = hash_device_password(device.password)

    # Adding update user and update date to input schema
    device = device.dict()
    device['created_by'] = device_to_update.created_by + '\n' + current_user.login
    device['created_at'] = device_to_update.created_at + '\n' + str(datetime.now())[0:16]

    # Saving changes to db
    device_to_update_query.update(device, synchronize_session=False)
    db.commit()

    return device_to_update_query.first()
