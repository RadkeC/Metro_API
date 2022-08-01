from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app import schemas, models, oauth2
from app.database import get_db
from app.utils import is_admin


router = APIRouter(
    prefix="/API",
    tags=['Groups']
)


# Group
@router.post('/group_create', status_code=status.HTTP_201_CREATED, response_model=schemas.Group_Response)
def group_create(group: schemas.Group_Create, db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    # Check if user is permissed to do that, if not raise 401 error
    is_admin(current_user)

    # Checking if group doesn't already exists
    if db.query(models.Group).filter(models.Group.name == group.name).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Group with name: "{group.name}" already exists')

    # Adding group to db with creating username and creating date
    new_group = models.Group(created_by=current_user.login, created_at=str(datetime.now())[0:16], **group.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group


@router.get('/group_get_all', status_code=status.HTTP_200_OK, response_model=List[schemas.Group_Response])
def group_get_all(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # SQLAlchemy question for get all groups
    groups = db.query(models.Group).order_by(models.Group.name).all()

    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Any group does not exists')

    return groups


@router.get("/group_get", status_code=status.HTTP_200_OK, response_model=schemas.Group_Response)
def group_get(name: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # SQLAlchemy question for get group by (name)
    group = db.query(models.Group).filter(models.Group.name == name).first()

    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with name: "{name}" does not exists')

    return group


@router.delete('/group_delete', status_code=status.HTTP_200_OK)
def group_delete(name: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Check if user is permissed to do that, if not raise 401 error
    is_admin(current_user)

    # SQLAlchemy question for get group to delete
    group = db.query(models.Group).filter(models.Group.name == name)

    if not group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with name: {name} does not exists')

    if db.query(models.Device).filter(models.Device.group_name == name).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Group with name: {name} have existing devices. '
                                   f'Edit or delete devices before deleting group')

    # Deleting group from db
    group.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted group: {name}"


@router.put('/group_update', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Group_Response)
def group_update(group: schemas.Group_Update, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    # Check if user is permissed to do that, if not raise 401 error
    is_admin(current_user)

    # SQLAlchemy question for get:
    #       group_to_update - group we want update;
    #       groups_to_names - list of groups to check unique name
    groups_to_names = db.query(models.Group).all()
    group_to_update_query = db.query(models.Group).filter(models.Group.id == group.id)
    group_to_update = group_to_update_query.first()

    if not group_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Group with id: "{group.id}" does not exists')

    # Create list of uniques variables for all groups
    names = [{'name': g.name, 'id': g.id} for g in groups_to_names]

    # Check if we don't change unique variable to used value
    for name in names:
        if group.name == name['name'] and group.id != name['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Group with name: "{group.name}" does already exists')

    # Changning group_name in devices that belong to this group if we change group name
    if group.name != group_to_update.name:
        devices = db.query(models.Device).filter(models.Device.group_name == group_to_update.name)
        for device in devices:
            device.group_name = group.name

    # Adding update user and update date to input schema
    group = group.dict()
    group['created_by'] = group_to_update.created_by + '\n' + str(current_user.login)
    group['created_at'] = group_to_update.created_at + '\n' + str(datetime.now())[0:16]

    # Saving changes to db
    group_to_update_query.update(group, synchronize_session=False)
    db.commit()

    return group_to_update
