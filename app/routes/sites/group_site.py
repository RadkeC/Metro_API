from fastapi import APIRouter, Request, status, Cookie, Depends
from fastapi.responses import RedirectResponse
import requests
from bs4 import BeautifulSoup
from json import loads as json_loads, dumps as json_dumps

from app.config import templates
from app.routes.sites.login_site import is_logged
from app.schemas import Group_Create, Group_Form, Buttons


router = APIRouter(
    prefix="",
    tags=['Group_site']
)


@router.get('/group_create', status_code=status.HTTP_200_OK)
def get_group_create(request: Request, token: str = Cookie(None)):
    print('get_group_create')
    user = is_logged(token, request)
    # Main case -> group create base design
    if user and user['admin']:
        content = {'username': user['login'],
                   'form': {'name': '', 'p1': '', 'p2': '', 'p3': '', 'p4': ''},
                   'mode': 'create',
                   'message': 'Każda grupa ma parametry podstawowe urządzeń: Nazwa, Model, Obiekt, Lokalizacja, '
                              'Ip, Maska, MAC, Login i Hasło. '
                              '\n W polach P1 - P4 wpisz nazwy dodatkowych parametrów tej grupy.'
                              '\n\n Niedozwolone jest używanie kombinacji <> '
                   }
        return templates.TemplateResponse("group_create.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    #  Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/group_create', status_code=status.HTTP_200_OK)
def post_group_create(request: Request,  token: str = Cookie(None),
                      create_form: Group_Create = Depends(Group_Create.as_form)):
    print('post_group_create')
    user = is_logged(token, request)
    # Main case
    if user and user['admin']:
        # Request to API to create group
        create_form = create_form.dict()
        data = json_dumps(create_form)
        req_response = requests.post(request.url_for('group_create'), headers={"Authorization": token}, data=data)

        # Changing None -> '' in p1-p4
        for p in ['p1', 'p2', 'p3', 'p4']:
            if not create_form[p]:
                create_form[p] = ''

        # Status code of response processing
        if req_response.status_code == 403:
            content = {'username': user['login'],
                       'form': create_form,
                       'mode': 'create',
                       'message': f'Każda grupa ma parametry podstawowe urządzeń: Nazwa, Model, Obiekt, Lokalizacja, '
                                  f'Ip, Maska, MAC, Login i Hasło. '
                                  f'\n W polach P1 - P4 wpisz nazwy dodatkowych parametrów tej grupy. '
                                  f'\n\n Niedozwolone jest używanie kombinacji <> '
                                  f'\n\n Grupa o nazwie "{create_form["name"]}" już istnieje.'
                       }
        elif req_response.status_code == 201:
            content = {'username': user['login'],
                       'form': {'name': '', 'p1': '', 'p2': '', 'p3': '', 'p4': ''},
                       'mode': 'create',
                       'message': f'Każda grupa ma parametry podstawowe urządzeń: Nazwa, Model, Obiekt, Lokalizacja, '
                                  f'Ip, Maska, MAC, Login i Hasło. '
                                  f'\n W polach P1 - P4 wpisz nazwy dodatkowych parametrów tej grupy. '
                                  f'\n\n Niedozwolone jest używanie kombinacji <> '
                                  f'\n\n Grupa "{create_form["name"]}" została pomyślnie utworzona.'
                       }
        else:
            content = {'username': user['login'],
                       'form': create_form,
                       'mode': 'create',
                       'message': f'Nieznany błąd danych. Proszę spróbować z innymi danymi.'
                       }

        return templates.TemplateResponse("group_create.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    #  Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/group_manage', status_code=status.HTTP_200_OK)
def get_group_manage(request: Request, token: str = Cookie(None)):
    print('get_group_manage')
    user = is_logged(token, request)
    # Main case
    if user:
        # Request to API to get list of group
        req_response = requests.get(request.url_for('group_get_all'), headers={"Authorization": token})
        if req_response.status_code == 404:
            content = {'username': user['login'],
                       'message': 'Nie istnieją żadne grupy. Utwórz grupę w karcie Grupy -> Utwórz'}
        elif req_response.status_code != 200:
            content = {'username': user['login'],
                       'message': 'Nieznany błąd'}
        else:
            data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
            # Change None -> '' in groups parameters, add Lp
            for n, row in enumerate(data):
                row['lp'] = n + 1
                for p in ['p1', 'p2', 'p3', 'p4']:
                    if not row[p]:
                        row[p] = ''
                    # Replace special symbol <> to \n
                    #else:
                    #    row[p] = row[p].replace('<>', '\n')

            content = {'username': user['login'],
                       'admin': user['admin'],
                       'table': data}

        return templates.TemplateResponse("group_manage.html", {'request': request, 'content': content})

    #  Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/group_manage', status_code=status.HTTP_200_OK)
def post_group_manage(request: Request, token: str = Cookie(None),
                      buttons: Buttons = Depends(Buttons.as_form),
                      update_form: Group_Form = Depends(Group_Form.as_form)):
    print('post_group_manage')
    user = is_logged(token, request)
    buttons = buttons.dict()
    # Main case
    if user and user['admin']:
        # Delete button case
        if buttons['delete_button']:
            # Request to API to delete group
            req_response = requests.delete(request.url_for('group_delete') + '?name=' + buttons['delete_button'],
                                           headers={"Authorization": token})

            # Status code of response processing
            if req_response.status_code == 404:
                content = {'username': user['login'],
                           'message': f'Grupa o nazwie {buttons["delete_button"]} nie istnieje.'}

            elif req_response.status_code == 403:
                content = {'username': user['login'],
                           'message': f' Grupa o nazwie {buttons["delete_button"]} ma przypisane urządzenia. '
                                      f' \n Usuń lub przenieś je do innych grup przed usunięciem.'
                                      f' Urządzenia -> Zarządzaj'}

            elif req_response.status_code == 200:
                return RedirectResponse(request.url_for(name='get_group_manage'), status_code=status.HTTP_303_SEE_OTHER)

            else:
                content = {'username': user['login'],
                           'message': 'Niezidentyfikowany błąd.'}

        # Edit button case
        elif buttons['edit_button']:
            # Request to API to get group from buttons['edit_button']
            req_response = requests.get(request.url_for('group_get') + '?name=' + buttons['edit_button'],
                                        headers={"Authorization": token})
            data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)

            # Change None -> '' in p1-p4
            for p in ['p1', 'p2', 'p3', 'p4']:
                if not data[p]:
                    data[p] = ''

            content = {'username': user['login'],
                       'admin': user['admin'],
                       'form': data,
                       'mode': 'edit',
                       'message': f'Każda grupa ma parametry podstawowe urządzeń: Nazwa, Model, Obiekt, Lokalizacja, '
                                  f'Ip, Maska, MAC, Login i Hasło. '
                                  f'\n W polach P1 - P4 wpisz nazwy dodatkowych parametrów tej grupy. '
                                  f'\n\n Niedozwolone jest używanie kombinacji <> '
                       }

            # Go to group_create template with 'edit mode'; different template is generate in same URL
            return templates.TemplateResponse("group_create.html", {'request': request, 'content': content})

        # Reject button case - return from group_create 'edit mode'
        elif buttons['reject_button']:
            return RedirectResponse(request.url_for(name='get_group_manage'), status_code=status.HTTP_303_SEE_OTHER)

        # Accept button case - from group_create 'edit mode'
        elif buttons['accept_button']:
            # Create JSON with data to create group
            update_form = update_form.dict()
            data = json_dumps(update_form)
            # Request to API to update group
            req_response = requests.put(request.url_for('group_update'), headers={"Authorization": token}, data=data)

            # Changing None -> '' in response
            for p in ['p1', 'p2', 'p3', 'p4']:
                if not update_form[p]:
                    update_form[p] = ''

            # Status code of response processing
            if req_response.status_code == 403:
                content = {'username': user['login'],
                           'form': update_form,
                           'mode': 'edit',
                           'message': f'Każda grupa ma parametry podstawowe urządzeń: Nazwa, Model, Obiekt, '
                                      f'Lokalizacja, Ip, Maska, MAC, Login i Hasło. '
                                      f'\n W polach P1 - P4 wpisz nazwy dodatkowych parametrów tej grupy. '
                                      f'\n\n Niedozwolone jest używanie kombinacji <> '
                                      f'\n\n Grupa o proponowanej nazwie już istnieje'}
                return templates.TemplateResponse("group_create.html", {'request': request, 'content': content})

            elif req_response.status_code == 422:
                update_form['name'] = ''
                content = {'username': user['login'],
                           'form': update_form,
                           'mode': 'edit',
                           'message': f'Każda grupa ma parametry podstawowe urządzeń: Nazwa, Model, Obiekt, '
                                      f'Lokalizacja, Ip, Maska, MAC, Login i Hasło. '
                                      f'\n W polach P1 - P4 wpisz nazwy dodatkowych parametrów tej grupy. '
                                      f'\n\n Niedozwolone jest używanie kombinacji <> '
                                      f'\n\n Brak obowiązkowego pola nazwa'}
                return templates.TemplateResponse("group_create.html", {'request': request, 'content': content})

            return RedirectResponse(request.url_for(name='get_group_manage'), status_code=status.HTTP_303_SEE_OTHER)

        else:
            content = {'username': user['login'],
                       'message': 'Niezidentyfikowany błąd. Jak tyś tu trafił człowieku.'}
        return templates.TemplateResponse("group_manage.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    #  Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)
