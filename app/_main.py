from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime
from typing import List

from app.database import get_db, engine
from app import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def start(db: Session = Depends(get_db)):
    n = models.Group(name='Radek', created_by='Ola')
    db.add(n)
    db.commit()
    db.refresh(n)
    return 2

# authorization - dodać automatyczny user
# Group
@app.post('/create_group', status_code=status.HTTP_201_CREATED, response_model=schemas.Group_Response)
def group_create(group: schemas.Group_Create, db: Session = Depends(get_db)):
    if group.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'You can not specify id when creating group')
    if db.query(models.Group).filter(models.Group.name == group.name).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Group with name "{group.name}" already exists')

    new_group = models.Group(created_by='Radke', created_at=str(datetime.now())[0:16], **group.dict()) # authorization
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group


@app.get("/group/{name}", status_code=status.HTTP_200_OK, response_model=schemas.Group_Response)
def group_get(name: str, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.name == name).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with name "{name}" does not exists')
    return group


@app.get('/group_all', status_code=status.HTTP_200_OK, response_model=List[schemas.Group_Response])
def group_get_all(db: Session = Depends(get_db)):
    groups = db.query(models.Group).order_by(models.Group.name).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Any group does not exists')

    return groups


@app.delete('/group_delete/{name}', status_code=status.HTTP_200_OK)
def group_delete(name: str, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.name == name)
    if not group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with name {name} does not exists')
    group.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted group {name}"


@app.put('/group_update', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Group_Response)
def group_update(updated_group: schemas.Group_Create, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == updated_group.id)
    if not group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with id "{updated_group.id}" does not exists')

    updated_group = updated_group.dict()
    updated_group['created_by'] = group.first().created_by + '\n' + 'Radek' # authorization
    updated_group['created_at'] = group.first().created_at + '\n' + str(datetime.now())[0:16]
    group.update(updated_group, synchronize_session=False)
    db.commit()

    return group.first()


# Device
@app.post('/create_device', status_code=status.HTTP_201_CREATED, response_model=schemas.Device_Response)
def device_create(device: schemas.Device_Create, db: Session = Depends(get_db)):
    """if group.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'You can not specify id when creating group')"""

    if db.query(models.Device).filter(models.Device.name == device.name).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with name "{device.name}" already exists')
    elif db.query(models.Device).filter(models.Device.ip == device.ip).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with ip "{device.ip}" already exists')
    elif db.query(models.Device).filter(models.Device.mac == device.mac).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Device with MAC "{device.mac}" already exists')
    group = db.query(models.Group).filter(models.Group.name == device.group_name).first()

    for [g, d] in [[group.p1, device.p1], [group.p2, device.p2], [group.p3, device.p3], [group.p4, device.p4]]:
        print(g, d)
        if g and not d:
            print('pierwszy')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Group require additional parameter from device. Add {g}.')
    if not group.p1:
        device.p1 = None     
    if not group.p2:
        device.p2 = None         
    if not group.p3:
        device.p3 = None         
    if not group.p4:
        device.p4 = None

    new_device = models.Device(created_by='Radke', created_at=str(datetime.now())[0:16], **device.dict()) # authorization
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device





"""@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post"""