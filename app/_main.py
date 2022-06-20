from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app import models
from app.routes import users, groups, devices, login

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(groups.router)
app.include_router(devices.router)
app.include_router(login.router)


@app.get("/", status_code=status.HTTP_200_OK)
def start(db: Session = Depends(get_db)):
    return {"message": "Welcome in Metro API"}



# doker ; heroku i git action


