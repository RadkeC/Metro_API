from fastapi import APIRouter, Request, Response, status, Form, Cookie
from fastapi.responses import RedirectResponse
import requests
from bs4 import BeautifulSoup
from json import loads as json_loads

from app.config import templates
from app.routes.sites.login_site import is_logged
from typing import  Optional
router = APIRouter(
    prefix="",
    tags=['Main_site']
)


@router.get("/", status_code=status.HTTP_200_OK)
def get_main(request: Request, token: str = Cookie(None)):
    print('get_main')
    if is_logged(token, request):
        return templates.TemplateResponse("main.html", {'request': request})
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)

