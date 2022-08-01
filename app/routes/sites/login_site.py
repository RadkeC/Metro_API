from fastapi import APIRouter, Request, Response, status, Form, Cookie
from fastapi.responses import RedirectResponse
import requests
from bs4 import BeautifulSoup
from json import loads as json_loads, dumps as json_dumps

from app.config import templates, settings


router = APIRouter(
    prefix="",
    tags=['Login_site']
)


# Function to check if user is logged - get user model with username and admin
def is_logged(token, request):
    # Request to API to check_token login.py
    req_response = requests.get(request.url_for('check_token'), headers={"Authorization": token})
    if req_response.status_code != 200:
        return None
    else:
        return json_loads(BeautifulSoup(req_response.text, 'html.parser').text)


@router.get("/login", status_code=status.HTTP_200_OK)
def get_login(request: Request, token: str = Cookie(None)):
    # Creating initial user if no users at all
    if requests.get(request.url_for('user_get_all'), headers={"Authorization": token}).status_code == 404:
        initial_user = {'admin': True, 'name': 'Initial', 'forename': 'Initial', 'department': 'Initial',
                        'login': settings.INITIAL_USER_LOGIN, 'password': settings.INITIAL_USER_PASSWORD}
        data = json_dumps(initial_user)
        requests.post(request.url_for('user_create'), headers={"Authorization": token}, data=data)

    if token:
        # If have token and its valid -> main page
        if is_logged(token, request):
            return RedirectResponse(request.url_for(name='get_main'), status_code=status.HTTP_303_SEE_OTHER)
        # If have token but it expired -> login page with massage
        else:
            return templates.TemplateResponse("login.html", {"request": request, "message": 'Sesja wygasła'})
    # If don't have token -> login page
    else:
        return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", status_code=status.HTTP_200_OK)
def post_login(request: Request, response: Response, username: str = Form(), password: str = Form()):
    print('post_login')
    # Request to API to check login and password -> get token in return
    req_response = requests.post(request.url_for('login'), data={"username": username, "password": password})
    if req_response.status_code != 202:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Błędne dane logowania"})

    # Create token variable
    data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
    token = {"Authorization": "Bearer " + data['access_token']}

    # Creating response with token cookie -> main page
    response = RedirectResponse(request.url_for(name='get_main'), status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="token", value=token['Authorization'], secure=True, httponly=True, samesite='none')
    return response
