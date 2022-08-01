from fastapi import APIRouter, Request, status, Cookie
from fastapi.responses import RedirectResponse

from app.config import templates
from app.routes.sites.login_site import is_logged


router = APIRouter(
    prefix="",
    tags=['Main_site']
)


@router.get("/", status_code=status.HTTP_200_OK)
def get_main(request: Request, token: str = Cookie(None)):
    print('get_main')
    user = is_logged(token, request)
    # Main case
    if user:
        content = {'username': user['login']}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    # Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
def get_logout(request: Request, token: str = Cookie(None)):
    print('get_logout')
    user = is_logged(token, request)
    # Response with delete cookie
    response = RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie('token', secure=True, httponly=True, samesite='none')
    return response
