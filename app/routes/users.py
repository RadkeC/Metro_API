from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app import schemas, models, oauth2
from app.database import get_db
from app.utils import hash_password


router = APIRouter(
    prefix="/API",
    tags=['Users']
)


# User
@router.post("/user_create", status_code=status.HTTP_201_CREATED, response_model=schemas.User_Response)
def user_create(user: schemas.User_Create, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # Checking if user with login in input schema don't exists
    if db.query(models.User).filter(models.User.login == user.login).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'User with login: "{user.login}" already exists')

    # Hashing user password -> utils.py and adding device to db
    new_user = models.User(created_by=current_user.login, created_at=str(datetime.now())[0:16], **user.dict())
    new_user.password = hash_password(new_user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/user_get_all", status_code=status.HTTP_200_OK, response_model=List[schemas.User_Response])
def user_get_all(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # SQLAlchemy question for get all users
    users = db.query(models.User).order_by(models.User.forename).all()

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="There are not any users profile created")

    return users


@router.get("/user_get", status_code=status.HTTP_200_OK, response_model=schemas.User_Response)
def user_get(login: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # SQLAlchemy question for get user object with login machting input value
    user = db.query(models.User).filter(models.User.login == login).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User: {login} does not exists")

    return user


@router.delete("/user_delete", status_code=status.HTTP_200_OK)
def user_delete(login: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # SQLAlchemy question for get user object we want delete
    user = db.query(models.User).filter(models.User.login == login)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User: {login} does not exists")

    # Deleting user from db
    user.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted user: {login}"


@router.put("/user_update", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.User_Response)
def user_update(user: schemas.User_Update, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # SQLAlchemy question for get:
    #       user_to_update - user object we want update;
    #       user_to_uniques - list of users to check unique login
    user_to_uniques = db.query(models.User).all()
    user_to_update_query = db.query(models.User).filter(models.User.id == user.id)
    user_to_update = user_to_update_query.first()

    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {user.id} does not exists")

    # Create list of uniques variables for all users
    logins = [{'login': u.login, 'id': u.id} for u in user_to_uniques]

    # Check if we don't change unique variable to used value
    for login in logins:
        if user.login == login['login'] and user.id != login['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'User with login: "{user.login}" does already exists')

    # Changning creating user in devices, groups and users that belong to this user if we change user login
    if user.login != user_to_update.login:
        # SQLAlchemy question for get all devices created/edited by this user
        devices = db.query(models.Device).filter(models.Device.created_by.like('%' + user_to_update.login + '%'))
        for device in devices:
            device.created_by = (user.login).join(device.created_by.split(user_to_update.login))
        # SQLAlchemy question for get all groups created/edited by this user
        groups = db.query(models.Group).filter(models.Group.created_by.like('%' + user_to_update.login + '%'))
        for group in groups:
            group.created_by = (user.login).join(group.created_by.split(user_to_update.login))
        # SQLAlchemy question for get all users created/edited by this user
        users = db.query(models.User).filter(models.User.created_by.like('%' + user_to_update.login + '%'))
        for use in users:
            use.created_by = (user.login).join(use.created_by.split(user_to_update.login))

    # Hashing password
    user.password = hash_password(user.password)

    # Adding update user and update date to input schema
    user = user.dict()
    user['created_by'] = user_to_update.created_by + '\n' + current_user.login
    user['created_at'] = user_to_update.created_at + '\n' + str(datetime.now())[0:16]
    # user['created_by'] = user_to_update.created_by
    # user['created_at'] = user_to_update.created_at

    # Saving changes to db
    user_to_update_query.update(user, synchronize_session=False)
    db.commit()

    return user_to_update
