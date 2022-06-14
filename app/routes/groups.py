from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime


from app.database import get_db
from app import schemas, models

router = APIRouter(
    prefix="",
    tags=['Groups']
)


# Group
@router.post('/group_create', status_code=status.HTTP_201_CREATED, response_model=schemas.Group_Response)
def group_create(group: schemas.Group_Create, db: Session = Depends(get_db)):
    if db.query(models.Group).filter(models.Group.name == group.name).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Group with name: "{group.name}" already exists')

    new_group = models.Group(created_by='Radke', created_at=str(datetime.now())[0:16], **group.dict()) # authorization
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group


@router.get("/group_get/{name}", status_code=status.HTTP_200_OK, response_model=schemas.Group_Response)
def group_get(name: str, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.name == name).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with name: "{name}" does not exists')
    return group


@router.get('/group_get_all', status_code=status.HTTP_200_OK, response_model=List[schemas.Group_Response])
def group_get_all(db: Session = Depends(get_db)):
    groups = db.query(models.Group).order_by(models.Group.name).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Any group does not exists')
    return groups


@router.delete('/group_delete/{name}', status_code=status.HTTP_200_OK)
def group_delete(name: str, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.name == name)
    if not group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with name: {name} does not exists')
    group.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted group: {name}"


@router.put('/group_update', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Group_Response)
def group_update(group: schemas.Group_Update, db: Session = Depends(get_db)):
    group_to_update = db.query(models.Group).filter(models.Group.id == group.id)
    if not group_to_update.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with id: "{group.id}" does not exists')

    group = group.dict()
    group['created_by'] = group_to_update.first().created_by + '\n' + 'Radek' # authorization
    group['created_at'] = group_to_update.first().created_at + '\n' + str(datetime.now())[0:16]
    group_to_update.update(group, synchronize_session=False)
    db.commit()

    return group_to_update.first()

