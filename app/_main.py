from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import models
from app.database import get_db, engine
from app.routes import users, groups, devices, login
from app.routes.sites import login_site, main_site, group_site, device_site, user_site


# Creating tables on base of models in db connected to app in table don't exists
models.Base.metadata.create_all(bind=engine)

# FastAPI instance and mounting folder with css files for templates
app = FastAPI()
app.mount('/static', StaticFiles(directory="app/static"), name="static")
app.mount('/app', StaticFiles(directory="app"), name="app")

# CORS - access from anywhere
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including API routes to app
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(devices.router)
app.include_router(login.router)

# Including pages routes to app
app.include_router(login_site.router)
app.include_router(main_site.router)
app.include_router(group_site.router)
app.include_router(device_site.router)
app.include_router(user_site.router)


@app.get("/API", status_code=status.HTTP_200_OK)
def start(db: Session = Depends(get_db)):
    return {"message": "Welcome in Metro API :)"}


# doker ; i git action
