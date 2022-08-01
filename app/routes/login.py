from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import schemas, models, utils, oauth2
from app.database import get_db


router = APIRouter(
    prefix="/API",
    tags=['Login']
)


# Login
@router.post('/login', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Token)
def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # SQLAlchemy question for get model.User object that match username in OAuth form -> oauth2.py
    user = db. query(models.User).filter(models.User.login == user_data.username).first()

    # User with login like username in OAuth form don't exists
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User with specified credentials does not exists")

    # Wrong password for user with login in OAuth form
    if not utils.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User with specified credentials does not exists")

    # Create JWT access token for properly logged user -> oauth2.py
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


# Path to get model.User object for logged user from other pages
@router.get('/login', status_code=status.HTTP_200_OK)
def check_token(current_user: str = Depends(oauth2.get_current_user)):
    return current_user


"""
    Function for possibly time validate token. 
    Need change in every path ,current_user: int = Depends(oauth2.get_current_user)' to 
    current_user: int = Depends(oauth2.get_current_user_authenticated).
    In outside application need first usage with token from '/login'.
    Have additional function in oauth2.py

@router.post('/login_authenticated', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Token)
def login_authenticated(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user_authenticated)):
    access_token = oauth2.create_access_token(data={"user_id": current_user.id})
    return {"access_token": access_token, "token_type": "bearer"}
"""

