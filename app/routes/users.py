from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app import schemas, models, oauth2
from app.utils import hash_password

router = APIRouter(
    prefix="/API",
    tags=['Users']
)


# User
@router.post("/user_create", status_code=status.HTTP_201_CREATED, response_model=schemas.User_Response)
def user_create(user: schemas.User_Create, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    if db.query(models.User).filter(models.User.login == user.login).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'User with login: "{user.login}" already exists')
    new_user = models.User(created_by=current_user.login, created_at=datetime.now(), **user.dict())
    new_user.password = hash_password(new_user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/user_get_all", status_code=status.HTTP_200_OK, response_model=List[schemas.User_Response])
def user_get_all(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    users = db.query(models.User).order_by(models.User.created_at).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="There are not any users profile created")
    return users


@router.get("/user_get/{login}", status_code=status.HTTP_200_OK, response_model=schemas.User_Response)
def user_get(login: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.login == login).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User: {login} does not exists")
    return user


@router.delete("/user_delete/{login}", status_code=status.HTTP_200_OK)
def user_delete(login: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.login == login)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User: {login} does not exists")
    user.delete(synchronize_session=False)
    db.commit()

    return f"Successfully deleted user: {login}"


@router.put("/user_update", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.User_Response)
def user_update(user: schemas.User_Update, db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    user_to_update_query = db.query(models.User).filter(models.User.id == user.id)
    user_to_update = user_to_update_query.first()
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {user.id} does not exists")

    if user.login != user_to_update.login:
        devices = db.query(models.Device).filter(models.Device.created_by == user_to_update.login)
        for device in devices:
            device.created_by = user.login
        groups = db.query(models.Group).filter(models.Group.created_by == user_to_update.login)
        for group in groups:
            group.created_by = user.login
        users = db.query(models.User).filter(models.User.created_by == user_to_update.login)
        for use in users:
            use.created_by = user.login

    user = user.dict()
    user['created_by'] = user_to_update.created_by
    user['created_at'] = user_to_update.created_at
    user_to_update_query.update(user, synchronize_session=False)
    db.commit()

    return user_to_update

