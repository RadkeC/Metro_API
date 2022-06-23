from fastapi import APIRouter, Request, Response, status, Form, Cookie
from fastapi.responses import RedirectResponse
import requests
from bs4 import BeautifulSoup
from json import loads as json_loads

from app.config import templates


router = APIRouter(
    prefix="",
    tags=['Login_site']
)


def is_logged(token, request):
    req_response = requests.get(request.url_for('check_token'), headers={"Authorization": token})
    if req_response.status_code == 200:
        return True
    else:
        return False


@router.get("/login", status_code=status.HTTP_200_OK)
def get_login(request: Request, token: str = Cookie(None)):
    if token:
        if is_logged(token, request):
            return RedirectResponse(request.url_for(name='get_main'), status_code=status.HTTP_303_SEE_OTHER)
        else:
            return templates.TemplateResponse("login.html", {"request": request, "message": 'Sesja wygasła'})
    else:
        return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", status_code=status.HTTP_200_OK)
def post_login(request: Request, response: Response, username: str = Form(), password: str = Form()):
    print('post_login')
    req_response = requests.post(request.url_for('login'), data={"username": username, "password": password})
    if req_response.status_code != 202:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Błędne dane logowania"})
    data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
    token = {"Authorization": "Bearer " + data['access_token']}

    response = RedirectResponse(request.url_for(name='get_main'), status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="token", value=token['Authorization'], secure=True, httponly=True, samesite='none')

    return response

