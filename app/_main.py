from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app import models
from app.routes import users, groups, devices, login
from app.routes.sites import login_site, main_site

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

app.include_router(login_site.router)
app.include_router(main_site.router)



@app.get("/API", status_code=status.HTTP_200_OK)
def start(db: Session = Depends(get_db)):
    return {"message": "Welcome in Metro API"}


from fastapi.responses import HTMLResponse, RedirectResponse, Response


from fastapi import Request, Form, Header, Cookie
from typing import Optional
import requests
import json
from bs4 import BeautifulSoup
from json import loads as json_loads



from typing import Union
@app.get("/main", status_code=status.HTTP_200_OK)
def main_menu_get(request: Request, token: Optional[str] = Cookie(None)):
    print(token)
    return 'get'
    #return templates.TemplateResponse("main_menu.html", {"request": request}, headers=header)


@app.post("/main", status_code=status.HTTP_200_OK)
def main_menu_post(request: Request, token: Optional[str] = Cookie(None)):
    #response = requests.get('http://127.0.0.1:8000' + app.url_path_for(name='user_get_all'))
    #print(response.status_code)
    print(token)
    #return templates.TemplateResponse("main_menu.html", {"request": request})
    return 'post'







@app.get('/q')
def q(request: Request, response: Response):
    response.set_cookie(key='qwe', value='asd', httponly=True)
    return True

@app.get('/w')
async def w(request: Request, response: Response, token: Optional[str] = Cookie(None)):
    print(token)
    print(type(token))
    return token








    """response = requests.get('http://127.0.0.1:8000' + app.url_path_for(name='group_get_all'),
                            headers={"Authorization": "Bearer " + data['access_token']})

    data = BeautifulSoup(response.text, 'html.parser')
    data = json_loads(data.text)
    print(data)"""

    """response = requests.post('http://127.0.0.1:8000' + app.url_path_for(name='group_create'),
                             json=x, headers={"Authorization": "Bearer " + data['access_token']})

    data = BeautifulSoup(response.text, 'html.parser')
    data = json_loads(data.text)
    print(data)"""




# doker ; i git action
