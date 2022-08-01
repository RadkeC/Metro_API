from fastapi import APIRouter, Request, status, Depends, Cookie, Form, File, UploadFile
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.background import BackgroundTasks
import requests
import shutil
import pandas as pd
import os

from bs4 import BeautifulSoup
from json import loads as json_loads, dumps as json_dumps
from time import sleep

from app.config import templates
from app.routes.sites.login_site import is_logged
from app.schemas import Device_Form, Resending_Data, Buttons


router = APIRouter(
    prefix="",
    tags=['Device_site']
)



# Helpful Tabs
device_parameters = [['name', 'on_name', 'exactly_name', 'Pełna nazwa urządzenia', 'Fragment nazwy urządzenia'],
                     ['model', 'on_model', 'exactly_model', 'Pełny numer modelu', 'Fragment numeru modelu'],
                     ['ob', 'on_ob', 'exactly_ob', 'Pełny symbol obiektu', 'Fragment symbolu obiektu'],
                     ['localization', 'on_localization', 'exactly_localization', 'Pełna nazwa lokalizacji',
                      'Fragment nazwy lokalizacji'],
                     ['ip', 'on_ip', 'exactly_ip', 'Pełny adres IP', 'Fragment adresu IP'],
                     ['mask', 'on_mask', 'exactly_mask', 'Pełna maska sieci', 'Fragment maski sieci'],
                     ['mac', 'on_mac', 'exactly_mac', 'Pełny adres MAC', 'Fragment adresu MAC'],
                     ['created_by', 'on_created_by', 'exactly_created_by', 'Stworzony przez:', 'Edytowany przez:'],
                     ['created_at', 'on_created_at', 'exactly_created_at', 'Stworzony: rrrr:mm:dd', 'Edtyowany: rrrr:mm:dd']]

titles = [{'title_name': 'Lp', 'title_var': 'lp'},
          {'title_name': 'Nazwa', 'title_var': 'name'},
          {'title_name': 'Model', 'title_var': 'model'},
          {'title_name': 'Obiekt', 'title_var': 'ob'},
          {'title_name': 'Lokalizacja', 'title_var': 'localization'},
          {'title_name': 'IP', 'title_var': 'ip'},
          {'title_name': 'Maska', 'title_var': 'mask'},
          {'title_name': 'MAC', 'title_var': 'mac'},
          {'title_name': 'Login', 'title_var': 'login'},
          {'title_name': 'Hasło', 'title_var': 'password'},
          {'title_name': 'Tworzący/Edytujący', 'title_var': 'created_by'},
          {'title_name': 'Stworzony/Edytowany', 'title_var': 'created_at'}]


# Function removing file for background task
def remove_file(path: str) -> None:
    sleep(3)
    os.unlink(path)


@router.get('/device_create', status_code=status.HTTP_200_OK)
def get_device_create(request: Request, token: str = Cookie(None)):
    print('get_device_create')
    user = is_logged(token, request)
    # Main case -> device create base design
    if user and user['admin']:
        # Load GROUPS list from db to create choose list
        req_response = requests.get(request.url_for('group_get_all'), headers={"Authorization": token})
        if req_response.status_code == 404:
            content = {'username': user['login'],
                       'message': 'Nie ma zdefiniowanych żadnych grup',
                       'mode': 'create'}
            return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

        groups_to_names = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
        # List with (groups) names
        groups = [g['name'] for g in groups_to_names]
        content = {'username': user['login'],
                   'selected_group': '',
                   'groups': groups,
                   'form': {'name': '', 'model': '', 'ob': '', 'localization': '', 'login': '', 'password': '',
                            'ip': '', 'mask': '', 'mac': '', 'group_name': '', 'p1': '', 'p2': '', 'p3': '', 'p4': ''},
                   'mode': 'create',
                   'message': 'Wymagania względem pliku:'
                              '\n\n Plik musi mieć rozszerzenie .xlsx o nazwach arkuszy odpowiadających grupom dodawanych urządzeń.'
                              '\n\n Zawartość arkuszy powinna wyglądać jak tabela z zakładki Urządzenia -> Zarządzaj dla danej grupy: kolumny od Nazwa do Hasło'
                   }

        return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

    # Not admin user case -> main page with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    # Unauthorized case -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/device_create', status_code=status.HTTP_200_OK)
def post_device_create(request: Request, token: str = Cookie(None), selected_group: str = Form(None),
                       buttons: Buttons = Depends(Buttons.as_form),
                       device_form: Device_Form = Depends(Device_Form.as_form)):
    print('post_device_create')
    user = is_logged(token, request)
    # Main case
    if user and user['admin']:
        # Returning to same page if blink option chosen from the list
        if not selected_group:
            return RedirectResponse(request.url_for(name='get_device_create'), status_code=status.HTTP_303_SEE_OTHER)

        # Load data from HTML form throught schemas and changed to dicts, None -> ''
        buttons = buttons.dict()
        device_form = device_form.dict()
        for key in device_form.keys():
            if not device_form[key]:
                device_form[key] = ''

        # Request to API to get list of created (groups), if no group exists back with massage
        req_response = requests.get(request.url_for('group_get_all'), headers={"Authorization": token})
        if req_response.status_code == 404:
            content = {'username': user['login'],
                       'message': 'Nie ma zdefiniowanych żadnych grup',
                       'mode': 'create'}
            return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

        groups = []
        groups_to_names = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
        for group in groups_to_names:
            groups.append(group['name'])
            # Creating dict containing titles of optional parameters selected group
            if group['name'] == selected_group:
                p_titles = {'p1': group['p1'], 'p2': group['p2'], 'p3': group['p3'], 'p4': group['p4']}

        content = {'username': user['login'],
                   'selected_group': selected_group,
                   'groups': groups,
                   'p': p_titles,
                   'form': device_form,
                   'mode': 'create',
                   'message': 'Dla parametrów dodatkowych (po polu Hasło jeśli skonfigurowano dodatkowe parametry dla wybranej grupy),'
                              ' można wprowadzić nową linię poprzez wprowadzenie kombinacji <>.'
                   }

        # No choise button was clicked case -> back to page with new content - changed design - show HTML form
        if not [x for x in buttons.values() if x != None]:
            return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

        # Accept button case
        elif buttons['accept_button']:
            # Creating JSON data to send request to API to create device
            for p in ['p1', 'p2', 'p3', 'p4']:
                if not device_form[p]:
                    device_form.pop(p)
            device_form['group_name'] = selected_group
            data = json_dumps(device_form)
            req_response = requests.post(request.url_for('device_create'), headers={"Authorization": token}, data=data)
            # Adding massage to content depending on response
            if req_response.status_code == 201:
                content['message'] = f'Dla parametrów dodatkowych (po polu Hasło jeśli skonfigurowano dodatkowe parametry dla wybranej grupy),'\
                                     f' można wprowadzić nową linię poprzez wprowadzenie kombinacji <>.' \
                                     f'\n\n Urządzenie: {device_form["name"]} zostało dodane do systemu'
            elif req_response.status_code == 403:
                content['message'] = f'Dla parametrów dodatkowych (po polu Hasło jeśli skonfigurowano dodatkowe parametry dla wybranej grupy),' \
                                 f' można wprowadzić nową linię poprzez wprowadzenie kombinacji <>.' \
                                 f'\n\n Urządzenie o podanych danych już istnieje. Pola nazwa, ip oraz mac muszą być unikatowe.'
            elif req_response == 404:
                content['message'] = f'Dla parametrów dodatkowych (po polu Hasło jeśli skonfigurowano dodatkowe parametry dla wybranej grupy),' \
                                 f' można wprowadzić nową linię poprzez wprowadzenie kombinacji <>.' \
                                 f'\n\n Wybrana grupa posiada wymagany parametr dowolny.'
            else:
                content['message'] = 'Nieznany błąd. Skontaktuj się z lekarzem lub farmaceutą.'
            # You stay in creating device page after successful creating new device
            return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})
        return 'Sygnał POST niewiadomego pochodzenia'

    # Not admin case -> main menu with massage
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    # Unauthorized user -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/device_manage', status_code=status.HTTP_200_OK)
def get_device_manage(request: Request, token: str = Cookie(None)):
    print('get_device_manage')
    user = is_logged(token, request)
    # Main case
    if user:
        # Request to API to get list of created (groups), if no group exists back with massage
        req_response = requests.get(request.url_for('group_get_all'), headers={"Authorization": token})
        if req_response.status_code == 404:
            content = {'username': user['login'],
                       'message': 'Nie ma zdefiniowanych żadnych grup',
                       'mode': 'create'}
            return templates.TemplateResponse("device_manage.html", {'request': request, 'content': content})

        groups_to_names = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
        # List of group is a dict bcs will be added selected_option in POST part
        groups = [{'name': g['name']} for g in groups_to_names]
        content = {'username': user['login'],
                   'selected_group': '',
                   'groups': groups,
                   'device_parameters': device_parameters,
                   'form': {'name': '', 'model': '', 'ob': '', 'localization': '', 'login': '', 'password': '',
                            'ip': '', 'mask': '', 'mac': '', 'group_name': '', 'p1': '', 'p2': '', 'p3': '', 'p4': ''},
                   'table': ''
                   }

        # Base design of manage device page
        return templates.TemplateResponse("device_manage.html", {'request': request, 'content': content})

    # Not admin case - unused bcs this page is commonly accessable
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    # Unauthorized user -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/device_manage', status_code=status.HTTP_200_OK)
def post_device_manage(request: Request, background_tasks: BackgroundTasks, token: str = Cookie(None),
                       selected_group: str = Form(None),
                       buttons: Buttons = Depends(Buttons.as_form),
                       device_form: Device_Form = Depends(Device_Form.as_form),
                       resending_data: Resending_Data = Depends(Resending_Data.as_form)):
    print('post_device_manage')
    user = is_logged(token, request)
    # Main case
    if user:
        # Request to API to get list of created (groups), if no group exists back with massage
        req_response = requests.get(request.url_for('group_get_all'), headers={"Authorization": token})
        if req_response.status_code == 404:
            content = {'username': user['login'],
                       'message': 'Nie ma zdefiniowanych żadnych grup',
                       'mode': 'create'}
            return templates.TemplateResponse("device_manage.html", {'request': request, 'content': content})

        groups_to_names = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
        # List of group is a dict bcs will be added selected_option in POST part
        groups = [{'name': g['name']} for g in groups_to_names]

        # Clearing resending value from None to 'None' conversion - changed None to '' in schemas so commented
        if resending_data.sorting == 'None':
            resending_data.sorting = ''

        # Butons case are here bcs they can change data before 'Show case' placed later
        # Check all/ Uncheck all button case
        if buttons.toggle_button:
            # We clear list anyway - list is in form of str bcs it backs from HTML form
            resending_data.selected_groups = []
            if buttons.toggle_button == 'check':
                # If it is check all option we make list full
                resending_data.selected_groups = '<>'.join([g['name'] for g in groups_to_names])

        # Sort button case
        elif buttons.sorting_button:
            # Get which sort button was clicked - table_name<>column_name<>asc/desc
            sorting_button = buttons.sorting_button.split('<>')
            # Get list of previous sorts from HTML hidden form field to redending data
            if resending_data.sorting:
                sort_list = resending_data.sorting.split('<>')
            else:
                sort_list = []
            # Check if that table have already sorting, if yes delete it
            for table in sort_list[::3]:
                if table == sorting_button[0]:
                    i = sort_list.index(table)
                    del sort_list[i:i+3]
            # Add sorting from button to other sorts
            if sort_list:
                sort_list = sort_list + sorting_button
            else:
                sort_list = sorting_button
            # Save to resending variable - will be used in Show case
            resending_data.sorting = '<>'.join(sort_list)

            buttons.show_button = 'show'

        # Delete button case
        elif buttons.delete_button and user['admin']:
            # Request to API to delete chosen device - device name in button variable -  if no device back with massage
            req_response = requests.delete(request.url_for('device_delete') + '?name=' + buttons.delete_button,
                                           headers={"Authorization": token})
            if req_response.status_code == 404:
                content = {'username': user['login'],
                           'message': f'Urządzenie o nazwie {buttons["delete_button"]} nie istnieje.'}
            # Succesful delete -> we will show table again on manage page
            elif req_response.status_code == 200:
                buttons.show_button = 'show'

        # Reject and accept case are accessable after edit case
        # Reject button case - abort edit device - edit case is later bcs it needs variables which will be created
        elif buttons.reject_button:
            buttons.show_button = 'show'
            # Filters unpacking to show table again - filters is hidden option of HTML form to send data between pages
            # '<>' combination is forbidden and is used to split string in program
            filters = resending_data.filters.split('<>')
            for n, attribute in enumerate(device_form.dict().keys()):
                device_form.__setattr__(attribute, filters[n])

        # Accept button case - edit device - edit case is later bcs it needs variables which will be created
        elif buttons.accept_button:
            # Creating JSON data from HTML form with added selected group and id of device
            update_form = device_form.dict()
            update_form['group_name'] = selected_group
            update_form['id'] = resending_data.id_form
            data = json_dumps(update_form)

            # Request to API to update device
            req_response = requests.put(request.url_for('device_update'), headers={"Authorization": token}, data=data)

            # We cleat None -> '' in case we will back to page with form data
            for p in update_form.keys():
                if not update_form[p]:
                    update_form[p] = ''

            # List of group. Its new variable bcs its didnt contain select_options,
            groups_in_edit = []
            for group in groups_to_names:
                groups_in_edit.append(group['name'])
                # Creating dict containing titles of optional parameters selected group
                if group['name'] == selected_group:
                    p_titles = {'p1': group['p1'], 'p2': group['p2'], 'p3': group['p3'], 'p4': group['p4']}
            # Creating variable containing data to send between pages - it will be hidden in HTML page
            content_to_resend = {'selected_groups': resending_data.selected_groups, 'filters': resending_data.filters,
                                 'y_offset': resending_data.y_offset, 'y_offset_div': resending_data.y_offset_div,
                                 'sorting': resending_data.sorting}

            if req_response.status_code == 403:
                content = {'username': user['login'],
                           'admin': user['admin'],
                           'selected_group': selected_group,
                           'groups': groups_in_edit,
                           'p': p_titles,
                           'form': update_form,
                           'content_to_resend': content_to_resend,
                           'mode': 'edit',
                           'message': 'Urządzenie o proponowanej nazwie, IP lub adresie MAC już istnieje'}
                return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

            elif req_response.status_code == 422:
                content = {'username': user['login'],
                           'admin': user['admin'],
                           'selected_group': selected_group,
                           'groups': groups_in_edit,
                           'p': p_titles,
                           'form': update_form,
                           'content_to_resend': content_to_resend,
                           'mode': 'edit',
                           'message': 'Brak wypełnionego pola obowiązkowego.'}
                return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

            # After successful edit we back to manage page and show table table. Filter options was sended through pages
            buttons.show_button = 'show'
            # filters unpacking to show table again
            filters = resending_data.filters.split('<>')
            for n, attribute in enumerate(device_form.dict().keys()):
                device_form.__setattr__(attribute, filters[n])

        # Force show case to create table before generating eksport file
        elif buttons.generate_button:
            buttons.show_button = 'show'


        # Creating selected_groups variable to resend clicked buttons. selected_groups is a string separated '<>'
        if resending_data.selected_groups:
            selected_groups = resending_data.selected_groups.split('<>')
        else:
            selected_groups = []

        # If group button clicked we add or remove group from selected_groups list
        if resending_data.group_checkbox:
            if resending_data.group_checkbox in selected_groups:
                selected_groups.pop(selected_groups.index(resending_data.group_checkbox))
            else:
                selected_groups.append(resending_data.group_checkbox)

        # We add select_option to groups list - dict
        for g in groups:
            if g['name'] in selected_groups:
                g['selected'] = 1
            else:
                g['selected'] = 0

        # Resending rightside of form (parameters), we change None -> ''
        device_form = device_form.dict()
        for key in device_form.keys():
            if not device_form[key]:
                device_form[key] = ''

        # Copy helpful tab from the start of this page
        device_parameters_local = device_parameters.copy()
        # If only 1 group is selected we will add optional parameters (p1-p4) to filter form
        if len(selected_groups) == 1:
            for group in groups_to_names:
                if selected_groups[0] == group['name']:
                    for p in ['p1', 'p2', 'p3', 'p4']:
                        if group[p]:
                            device_parameters_local.append([p, 'on_'+p, 'exactly_'+p, 'Dokładny: '+group[p],
                                                            'Fragment: '+group[p]])

        # Show button case devices
        table = []
        if buttons.show_button:
            # Creating url parameter with constraits
            url = request.url_for('device_get') + '?'
            for parameter in device_parameters_local:
                # IS ON_
                if device_form[parameter[1]]:
                    # IS EXACTLY_
                    if device_form[parameter[2]]:
                        if not parameter[0] in ['created_by', 'created_at']:
                            url = url + parameter[0] + '=' + device_form[parameter[0]] + '&'
                        # EXCEPTION OF CREATED_BY AND CREATED_AT - CREATED NOT EDITED
                        else:
                            url = url + parameter[0] + '=' + device_form[parameter[0]] + '%&'
                    # IS NOT EXACTLY_
                    else:
                        url = url + parameter[0] + '=%' + device_form[parameter[0]] + '%&'

            # List of sorted columns from resending data in HTML - group<>column<>asc/desc ...
            if resending_data.sorting:
                sort_list = resending_data.sorting.split('<>')
            else:
                sort_list = []

            # Requesting API and creating table
            if selected_groups:
                # Coulter for Lp. of devices
                i = 0
                # For every selected group different table
                for group in selected_groups:
                    # Copy helpful tab from the start of this page
                    titles_local = titles.copy()
                    # FINDING ADDITIONAL PARAMETERS P1-P4
                    for g in groups_to_names:
                        if group == g['name']:
                            for p in ['p1', 'p2', 'p3', 'p4']:
                                if g[p]:
                                    # Adding optional parameters to helpful tab
                                    titles_local.insert(-4, {'title_name': g[p], 'title_var': p})

                    # Find if group from for loop is in sort list - group<>column<>asc/desc ...
                    if group in sort_list[::3]:
                        sort_by = sort_list[sort_list.index(group) + 1]
                        sort_way = sort_list[sort_list.index(group) + 2]
                    else:
                        sort_by = 'name'
                        sort_way = 'asc'
                    # Adding sort to url request
                    url = url + 'sort_by=' + sort_by + '&sort_way=' + sort_way + '&'

                    # Creating variable to design sorting buttons in HTML

                    # Request to API to get devices of group from for loop
                    req_response = requests.get(url + 'group_name=' + group, headers={"Authorization": token})
                    # Information if group is empty
                    if req_response.status_code == 404:
                        table.append({'table_name': group, 'table_content': None})
                    else:
                        data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
                        # Adding Lp to device's, None -> '' in p1-p4 and replace separator '<>' to '\n'
                        for n, row in enumerate(data):
                            i = i + 1
                            row['lp'] = i
                            for p in ['p1', 'p2', 'p3', 'p4']:
                                if not row[p]:
                                    row[p] = ''
                                #else:
                                #    row[p] = row[p].replace('<>', '\n')
                        # Creating list of table dicts - will be added to content later
                        table.append({'table_name': group, 'table_content': data, 'table_title': titles_local,
                                      'sort_by': sort_by, 'sort_way': sort_way})

            # If user didn't check groups (want all groups)
            #else:
            #    req_response = requests.get(url + 'group_name=' + group, headers={"Authorization": token})

        # Generate button case - export xlsx file
        if buttons.generate_button:
            error = True
            for tab in table:
                if tab['table_content']:
                    error = False
            if error:
                # Content with table - from show case - showing user devices tables
                content = {'username': user['login'],
                           'admin': user['admin'],
                           'selected_groups': '<>'.join(selected_groups),
                           'sorting': resending_data.sorting,
                           'y_offset': resending_data.y_offset,
                           'y_offset_div': resending_data.y_offset_div,
                           'groups': groups,
                           'device_parameters': device_parameters_local,
                           'form': device_form,
                           'table': table,
                           'message': 'Aby eksportować dane należy wybrać co najmniej jedną nie pustą grupę'
                           }

                return templates.TemplateResponse("device_manage.html", {'request': request, 'content': content})

            export_data = []
            # New sheet for anyone not empty table
            for sheet in table:
                if sheet['table_content']:
                    sheet_dict = {}

                    # Creating dict to create pd.DataFrame - {column_name1: [var1, var2, ...],column_name2: [var1]}
                    for title in sheet['table_title']:
                        # We don't get lp column bcs its not data from database
                        if title['title_name'] != 'Lp':
                            sheet_dict[title['title_name']] = []
                            # For each row in table we search par equal to column_name, title: 'Nazwa' - 'name'
                            for row in sheet['table_content']:
                                sheet_dict[title['title_name']].append(row[title['title_var']])

                    # Creating DataFrame from dict and changing index to start from 1
                    df = pd.DataFrame(sheet_dict)
                    df.index += 1

                    # Colective variable for all tables
                    export_data.append({'sheet_name': sheet['table_name'], 'sheet_data': df})

            # We create exel file and save any table as separate sheet
            with pd.ExcelWriter('Metro_API.xlsx') as writer:
                for sheet_to_exel in export_data:
                    sheet_to_exel['sheet_data'].to_excel(writer, sheet_name=sheet_to_exel['sheet_name'])

            # Removing file after sending - used function from start of this page; background_task in def of this patf
            background_tasks.add_task(remove_file, './Metro_API.xlsx')

            # We return file to download
            return FileResponse('./Metro_API.xlsx',
                                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                filename='Metro_API.xlsx')

        # Edit button case - isn't with other button cases bcs need variables created later - blocked for not admin
        elif buttons.edit_button and user['admin']:
            # Request to API to get data od editing device
            req_response = requests.get(request.url_for('device_get') + '?name=' + buttons.edit_button,
                                        headers={"Authorization": token})
            # [0] bcs in device_get we have .all() not .first() like in groups
            data = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)[0]

            # None -> ''
            for p in ['p1', 'p2', 'p3', 'p4']:
                if not data[p]:
                    data[p] = ''

            # Creating list og groups - not dict with selected_options
            groups_in_edit = []
            for group in groups_to_names:
                groups_in_edit.append(group['name'])
                # Creating dict containing titles of optional parameters selected group
                if group['name'] == data['group_name']:
                    p_titles = {'p1': group['p1'], 'p2': group['p2'], 'p3': group['p3'], 'p4': group['p4']}

            # Creating (filters) to send rightside options through pages - str separated '<>'
            filters = ''
            for key in device_form.keys():
                filters = filters + device_form[key] + '<>'

            # Data sended between pages
            content_to_resend = {'selected_groups': '<>'.join(selected_groups), 'filters': filters[:-2],
                                 'y_offset': resending_data.y_offset, 'y_offset_div': resending_data.y_offset_div,
                                 'sorting': resending_data.sorting}

            content = {'username': user['login'],
                       'admin': user['admin'],
                       'selected_group': data['group_name'],
                       'sorting': resending_data.sorting,
                       'groups': groups_in_edit,
                       'p': p_titles,
                       'form': data,
                       'content_to_resend': content_to_resend,
                       'mode': 'edit'}

            # We render page based on device_create with edit mode
            return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

        # Content with table - from show case - showing user devices tables
        content = {'username': user['login'],
                   'admin': user['admin'],
                   'selected_groups': '<>'.join(selected_groups),
                   'sorting': resending_data.sorting,
                   'y_offset': resending_data.y_offset,
                   'y_offset_div': resending_data.y_offset_div,
                   'groups': groups,
                   'device_parameters': device_parameters_local,
                   'form': device_form,
                   'table': table}

        return templates.TemplateResponse("device_manage.html", {'request': request, 'content': content})

    # Unauthorized user -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/load_from_file')
def post_load_from_file(request: Request, token: str = Cookie(None), load_from_file: UploadFile = File(...)):
    print('post_load_from_file')
    user = is_logged(token, request)
    # Main case
    if user and user['admin']:
        raport = []
        # Request to API to get list of created (groups), if no group exists back with massage
        req_response = requests.get(request.url_for('group_get_all'), headers={"Authorization": token})
        if req_response.status_code == 404:
            content = {'username': user['login'],
                       'message': 'Nie ma zdefiniowanych żadnych grup',
                       'mode': 'create'}
            return templates.TemplateResponse("device_create.html", {'request': request, 'content': content})

        groups_to_names = json_loads(BeautifulSoup(req_response.text, 'html.parser').text)
        # List of group
        groups = [g['name'] for g in groups_to_names]

        # Make copy of User file
        with open(f'{load_from_file.filename}', "wb") as buffer:
            shutil.copyfileobj(load_from_file.file, buffer)

        # Open copied file and get names of sheets, close file after
        file = pd.ExcelFile(os.path.abspath(f'{load_from_file.filename}'))
        sheets = file.sheet_names
        file.close()

        # Create raport_file for user download
        with open('raport.txt', 'w') as raport_file:

            # We iter through sheets (groups)
            for sheet in sheets:
                # If sheet_name is in group list
                if sheet in groups:
                    # Adding information that sheetname found in groupl list to raport
                    raport_file.write(f"\n Grupa: {sheet} \n")
                    raport.append('<br>')
                    raport.append(f'Grupa: {sheet}')
                    raport.append('<br>')
                    # Load data from sheet
                    df = pd.read_excel(io=load_from_file.filename, sheet_name=sheet)

                    # List of parameters of group in sheetname
                    group = groups_to_names[groups.index(sheet)]
                    # Creating dict of expected titles in the sheet
                    titles_local = titles.copy()
                    titles_local.pop(0)
                    del titles_local[-2:]

                    for p in ['p1', 'p2', 'p3', 'p4']:
                        if group[p]:
                            titles_local.insert(-2, {'title_name': group[p], 'title_var': p})

                    error = False
                    # Getting list of column titles from sheet
                    headers = df.head(0)
                    # Checking if column titles matches expecting titles
                    for n, head in enumerate(headers):
                        if head != titles_local[n]['title_name']:
                            raport_file.write(f"\n\tNiewłaściwe nagłówki dla grupy {sheet}")
                            raport.append(f'Niewłaściwe nagłówki dla grupy {sheet}')
                            error = True

                    # If titles are ok we start adding devices
                    if not error:
                        # Changing df to list
                        lines = df.values.tolist()
                        for line in lines:
                            # Creating device dict for request API
                            device = {'group_name': sheet}
                            for n, parameter in enumerate(titles_local):
                                device[parameter['title_var']] = line[n]

                            data = json_dumps(device)
                            req_response = requests.post(request.url_for('device_create'), headers={"Authorization": token},
                                                         data=data)
                            # Adding infos to raport
                            if req_response.status_code == 201:
                                raport_file.write(f'\n\tSukces - urządzenie: {device["name"]}')
                                raport.append(f'Sukces - urządzenie: {device["name"]}')
                            elif req_response.status_code == 403:
                                raport_file.write(f'\n\tPorażka - urządzenie: {device["name"]} - powtarzające się Nazwa, IP lub MAC')
                                raport.append(f'Porażka - urządzenie: {device["name"]} - powtarzające się Nazwa, IP lub MAC')
                            elif req_response.status_code == 422:
                                raport_file.write(f'\n\tPorażka - urządzenie: {device["name"]} - niewłaściwe dane wejściowe')
                                raport.append(f'Porażka - urządzenie: {device["name"]} - niewłaściwe dane wejściowe')
                            else:
                                raport_file.write(f'\n\tPorażka - urządzenie: {device["name"]} - nieznany błąd')
                                raport.append(f'Porażka - urządzenie: {device["name"]} - nieznany błąd')
                    raport_file.write(f'\n')

        # Delete copy of file
        os.remove(os.path.abspath(f'{load_from_file.filename}'))

        content = {'username': user['login'],
                   'selected_group': '',
                   'groups': groups,
                   'form': {'name': '', 'model': '', 'ob': '', 'localization': '', 'login': '', 'password': '',
                            'ip': '', 'mask': '', 'mac': '', 'group_name': '', 'p1': '', 'p2': '', 'p3': '', 'p4': ''},
                   'mode': 'create',
                   'raport': raport}

        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    # Not admin case - unused bcs this page is commonly accessable
    elif user:
        content = {'username': user['login'],
                   'message': 'Wyberana operacja wymaga uprawnień administratora'}
        return templates.TemplateResponse("base.html", {'request': request, 'content': content})

    # Unauthorized user -> login page
    else:
        return RedirectResponse(request.url_for(name='get_login'), status_code=status.HTTP_303_SEE_OTHER)


@router.post('/raport')
def post_raport(request: Request, background_tasks: BackgroundTasks, token: str = Cookie(None)):
    print('post_raport')
    user = is_logged(token, request)
    if user:
        if os.path.exists('./raport.txt'):
            # Delete raport.txt after send
            #background_tasks.add_task(remove_file, './raport.txt')
            # Return raport_file to user
            return FileResponse('./raport.txt', media_type='text/plain', filename='raport.txt')
        else:
            return templates.TemplateResponse("base.html", {'request': request, 'content': {'username': user['login']}})


