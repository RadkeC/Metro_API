from fastapi import APIRouter, Request, status, Cookie, Depends
from fastapi.responses import RedirectResponse
import requests

from bs4 import BeautifulSoup
from json import loads as json_loads, dumps as json_dumps

from app.config import templates
from app.routes.sites.login_site import is_logged
from app.schemas import User_Create, User_Form, Buttons


router = APIRouter(
    prefix="",
    tags=['User_site']
)


@router.get('/user_create', status_code=status.HTTP_200_OK)
def get_user_create(request: Request, token: str = Cookie(None)):
    print('get_user_create')
    user = is_logged(token, request)
    # Main case -> user create base design
    if user and user['admin']:
        content = {'username': user['login'],
                   'form': {'admin': '', 'name': '', 'forename': '', 'department': '', 'login': '', 'password': ''},
                   'mode': 'create'
                   }

        return templates.TemplateResponse("user_create.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    # Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/user_create', status_code=status.HTTP_200_OK)
def post_user_create(request: Request, token: str = Cookie(None),
                     user_form: User_Create = Depends(User_Create.as_form)):
    print('post_user_create')
    user = is_logged(token, request)
    # Main case
    if user and user['admin']:
        # Request to API to create user
        create_form = user_form.dict()
        data = json_dumps(create_form)
        req_response = requests.post(request.url_for('user_create'), headers={"Authorization": token}, data=data)

        # Status code of response processing
        if req_response.status_code == 403:
            content = {'username': user['login'],
                       'form': create_form,
                       'mode': 'create',
                       'message': f'Urzytkownik o loginie: "{create_form["login"]}" już istnieje.'
                       }
        elif req_response.status_code == 201:
            content = {'username': user['login'],
                       'form': {'admin': '', 'name': '', 'forename': '', 'department': '', 'login': '', 'password': ''},
                       'mode': 'create',
                       'message': f'Urzytkownik: "{create_form["login"]}" został pomyślnie dodany.'
                       }
        else:
            content = {'username': user['login'],
                       'form': create_form,
                       'mode': 'create',
                       'message': f'Nieznany błąd danych. Proszę spróbować z innymi danymi.'
                       }

        return templates.TemplateResponse("user_create.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    #  Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/user_manage', status_code=status.HTTP_200_OK)
def get_user_manage(request: Request, token: str = Cookie(None)):
    user = is_logged(token, request)
    # Main case
    if user:
        # Request to API to get list of users
        req_response = requests.get(request.url_for('user_get_all'), headers={"Authorization": token})
        if req_response.status_code == 404:
            content = {'username': user['login'],
                       'message': 'Nie istnieją żadni urzytkownicy. Dodaj urzytkwników w karcie Urzytkownicy -> Dodaj'}
        elif req_response.status_code != 200:
            content = {'username': user['login'],
                       'message': 'Nieznany błąd'}
        else:
            data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)

            # Change None -> '' in groups parameters, add Lp
            for n, row in enumerate(data):
                row['lp'] = n + 1

            content = {'username': user['login'],
                       'admin': user['admin'],
                       'table': data}

        return templates.TemplateResponse("user_manage.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    #  Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/user_manage', status_code=status.HTTP_200_OK)
def post_user_manage(request: Request, token: str = Cookie(None),
                     buttons: Buttons = Depends(Buttons.as_form),
                     update_form: User_Form = Depends(User_Form.as_form)):
    print('post_user_manage')
    user = is_logged(token, request)
    buttons = buttons.dict()
    # Main case
    if user and user['admin']:
        # Delete button case
        if buttons['delete_button']:
            # Request to API to delete user
            req_response = requests.delete(request.url_for('user_delete') + '?login=' + buttons['delete_button'],
                                           headers={"Authorization": token})

            # Status code of response processing
            if req_response.status_code == 404:
                content = {'username': user['login'],
                           'message': f'Urzytkownik o loginie: {buttons["delete_button"]} nie istnieje.'}

            elif req_response.status_code == 200:
                return RedirectResponse(request.url_for(name='get_user_manage'), status_code=status.HTTP_303_SEE_OTHER)

            else:
                content = {'username': user['login'],
                           'message': 'Niezidentyfikowany błąd.'}

        # Edit button case
        elif buttons['edit_button']:
            # Request to API to get user data from buttons['edit_button']
            req_response = requests.get(request.url_for('user_get') + '?login=' + buttons['edit_button'],
                                        headers={"Authorization": token})
            data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
            data['password'] = ''

            content = {'username': user['login'],
                       'admin': user['admin'],
                       'form': data,
                       'mode': 'edit'
                       }

            # Go to group_create template with 'edit mode'; different template is generate in same URL
            return templates.TemplateResponse("user_create.html", {'request': request, 'content': content})

        # Reject button case - return from group_create 'edit mode'
        elif buttons['reject_button']:
            return RedirectResponse(request.url_for(name='get_user_manage'), status_code=status.HTTP_303_SEE_OTHER)

        # Accept button case - from group_create 'edit mode'
        elif buttons['accept_button']:
            # Create JSON with data to create group
            update_form = update_form.dict()
            data = json_dumps(update_form)

            print(data)
            # Request to API to update group
            req_response = requests.put(request.url_for('user_update'), headers={"Authorization": token}, data=data)

            # Status code of response processing
            if req_response.status_code == 403:
                content = {'username': user['login'],
                           'form': update_form,
                           'mode': 'edit',
                           'message': 'Urzytkownik o proponowanym loginie już istnieje'}
                return templates.TemplateResponse("user_create.html", {'request': request, 'content': content})

            elif req_response.status_code == 422:
                for key in update_form.keys():
                    if not update_form[key]:
                        update_form[key] = ''
                content = {'username': user['login'],
                           'form': update_form,
                           'mode': 'edit',
                           'message': 'Brak obowiązkowego pola'}
                return templates.TemplateResponse("user_create.html", {'request': request, 'content': content})

            return RedirectResponse(request.url_for(name='get_user_manage'), status_code=status.HTTP_303_SEE_OTHER)

        else:
            content = {'username': user['login'],
                       'message': 'Niezidentyfikowany błąd. Jak tyś tu trafił człowieku.'}
        return templates.TemplateResponse("user_manage.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    #  Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/user_my', status_code=status.HTTP_200_OK)
def get_user_my(request: Request, token: str = Cookie(None)):
    return 'not now'
