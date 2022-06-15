from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from app.database import get_db
from app import schemas, models, utils, oauth2

router = APIRouter(
    prefix="",
    tags=['Login']
)
import fastapi.security.oauth2 as zxc

zxc.OAuth2PasswordRequestForm

# Login
@router.post('/login', status_code=status.HTTP_202_ACCEPTED)#, response_model=schemas.Token)
def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #OAuth2PasswordRequestForm : {"username": , "password": }

    user = db. query(models.User).filter(models.User.login == user_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User with specified credentials does not exists")

    if not utils.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User with specified credentials does not exists")

    # token
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
