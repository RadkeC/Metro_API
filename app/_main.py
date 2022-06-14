from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app import models
from app.routes import users, groups, devices

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(groups.router)
app.include_router(devices.router)


def is_admin(login, db):
    if not db.query(models.User).filter(models.User.login == login).first().admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Logged user has not permission to perform that action")


@app.get("/", status_code=status.HTTP_200_OK)
def start(db: Session = Depends(get_db)):
    return {"message": "Welcome in Metro API"}


                        # authorization - dodać automatyczny user
#autentication
#hasshowanie haseł
#logowanie
#middleware - dostęp do api poprzez każdy url
#alembic i doker ; heroku i git action


