import pytest

from app import schemas


###################################################### INIT TEST
def test_group_init(client, test_user, test_user_admin, test_user_var, test_groups_dict, test_devices_dict):
    res = client.get("/API")
    assert res.status_code == 200

    assert test_user['login'] == 'User1_login'
    assert test_user_admin['login'] == 'User2_login' and test_user_admin['admin']
    assert test_user_var['login'] == 'User3_login'

    assert len(test_groups_dict) == 2
    assert len(test_devices_dict) == 4
    assert test_devices_dict[0]['group_name'] == test_groups_dict[0]['name'] and \
           test_devices_dict[1]['group_name'] == test_groups_dict[0]['name']
    assert test_devices_dict[2]['group_name'] == test_groups_dict[1]['name'] and \
           test_devices_dict[3]['group_name'] == test_groups_dict[1]['name']


def test_group_init_models_groups(test_groups):
    assert len(test_groups) == 2
    assert test_groups[0].name == 'Grupa 1' and test_groups[1].name == 'Grupa 2'


def test_group_init_models_groups_and_devices(test_groups_and_devices):
    [test_groups, test_devices] = test_groups_and_devices

    assert len(test_groups) == 2
    assert len(test_devices) == 4
    assert test_devices[0].group_name == test_groups[0].name and test_devices[1].group_name == test_groups[0].name
    assert test_devices[2].group_name == test_groups[1].name and test_devices[3].group_name == test_groups[1].name
    assert test_groups[0].name == 'Grupa 1' and test_groups[1].name == 'Grupa 2'
    assert test_devices[0].name == 'device 1' and test_devices[1].name == 'device 2' and \
           test_devices[2].name == 'device 3' and test_devices[3].name == 'device 4'


####################################################### CREATE
@pytest.mark.parametrize("group_number, device_additional_params", [
    (0, {}),
    (1, {"p1": "par1dev_test", "p2": "par2dev_test", "p3": "par3dev_test", "p4": "par4dev_test"})])
def test_device_create(authorized_client_admin, test_groups, group_number, device_additional_params):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": test_groups[group_number].name}
    device_data.update(device_additional_params)

    res = authorized_client_admin.post("/API/device_create", json=device_data)
    new_device = schemas.Device_Response(**res.json())

    assert res.status_code == 201
    assert new_device.name == device_data['name'] and new_device.group_name == device_data['group_name']


@pytest.mark.parametrize("duplicated_parametr", [
    ('name'),
    ('ip'),
    ('mac')])
def test_device_create_duplicate(authorized_client_admin, test_groups_dict, test_devices_dict, duplicated_parametr):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": 'Grupa_test'}

    device_data[duplicated_parametr] = test_devices_dict[0][duplicated_parametr]
    device_data['group_name'] = test_groups_dict[0]['name']

    res = authorized_client_admin.post("/API/device_create", json=device_data)

    assert res.status_code == 403
    assert device_data[duplicated_parametr] in res.json()['detail']


def test_device_create_not_existing_group(authorized_client_admin, test_groups):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": 'Grupa_test'}

    res = authorized_client_admin.post("/API/device_create", json=device_data)

    assert res.status_code == 404
    assert device_data['group_name'] in res.json()['detail']


def test_device_create_missing_additional_parameters(authorized_client_admin, test_groups):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": test_groups[1].name}

    res = authorized_client_admin.post("/API/device_create", json=device_data)
    assert res.status_code == 404
    assert 'Group require additional parameter from device' in res.json()['detail']


def test_device_create_wrong_input(authorized_client_admin):
    res = authorized_client_admin.post("/API/device_create", json=7)
    assert res.status_code == 422


####################################################### GET
@pytest.mark.parametrize("dict_of_sorting_parameters, dict_of_results", [
    ({'name': 'device 1'}, {'device_count': 1, 'first_device': 'device 1'}),
    ({"model": "model 1"}, {'device_count': 2, 'first_device': 'device 1'}),
    ({"ob": "ob 1"}, {'device_count': 2, 'first_device': 'device 1'}),
    ({"localization": "lokalizacja 1"}, {'device_count': 4, 'first_device': 'device 1'}),
    ({"login": "login 1"}, {'device_count': 4, 'first_device': 'device 1'}),
    ({"password": "password1"}, {'device_count': 4, 'first_device': 'device 1'}),
    ({"ip": "ip1"}, {'device_count': 1, 'first_device': 'device 1'}),
    ({"mask": "mask1"}, {'device_count': 1, 'first_device': 'device 1'}),
    ({"mac": "mac1"}, {'device_count': 1, 'first_device': 'device 1'}),
    ({"created_by": 'User2_login'}, {'device_count': 4, 'first_device': 'device 1'}),
    ({"created_at": "2023-03-10 09:13"}, {'device_count': 4, 'first_device': 'device 1'}),
    ({"group_name": 'Grupa 1'}, {'device_count': 2, 'first_device': 'device 1'}),
    ({"p1": "par1dev3", "group_name": 'Grupa 2'}, {'device_count': 1, 'first_device': 'device 3'}),
    ({"p2": "par2dev3", "group_name": 'Grupa 2'}, {'device_count': 1, 'first_device': 'device 3'}),
    ({"p3": "par3dev3", "group_name": 'Grupa 2'}, {'device_count': 1, 'first_device': 'device 3'}),
    ({"p4": "par4dev3", "group_name": 'Grupa 2'}, {'device_count': 1, 'first_device': 'device 3'}),
    ({"model": "model 1", "ob": "ob 1"}, {'device_count': 1, 'first_device': 'device 1'}),
    ({"localization": "lokalizacja 1", 'sort_by': 'ip', 'sort_way': 'desc'},
     {'device_count': 4, 'first_device': 'device 4'}),
    ({"localization": "lokalizacja 1", 'sort_by': 'ip', 'sort_way': 'asc'},
     {'device_count': 4, 'first_device': 'device 1'})])
def test_device_get(authorized_client_admin, test_groups_and_devices, dict_of_sorting_parameters, dict_of_results):
    path_var = "/API/device_get?"
    for key in dict_of_sorting_parameters.keys():
        splited_word = dict_of_sorting_parameters[key].split(' ')
        path_var += key + '=' + '%20'.join(splited_word) + '&'
    path_var = path_var[:-1]

    res = authorized_client_admin.get(path_var)
    devices_list = []
    for device in res.json():
        devices_list.append(schemas.Device_Response(**device))

    assert res.status_code == 200
    assert len(devices_list) == dict_of_results['device_count']
    assert devices_list[0].name == dict_of_results['first_device']


def test_device_get_no_existing(authorized_client_admin, test_groups_and_devices):
    test_devices = test_groups_and_devices[1]
    res = authorized_client_admin.get(f"/API/device_get?name={test_devices[0].name}&ip={test_devices[1].ip}")

    assert res.status_code == 404
    assert 'There are not any devices with specified constraints' in res.json()['detail']


def test_device_get_wrong_input(authorized_client_admin, test_devices_dict):
    res = authorized_client_admin.get("/API/device_get", json=7)
    assert res.status_code == 200
    # Sending wrong input result in requesting all devices


####################################################### GET ALL
def test_device_get_all(authorized_client_admin, test_devices_dict):
    res = authorized_client_admin.get("/API/device_get_all")

    assert res.status_code == 200
    assert len(res.json()) == len(test_devices_dict)


def test_device_get_all_not_existing(authorized_client_admin):
    res = authorized_client_admin.get("/API/device_get_all")

    assert res.status_code == 404
    assert 'There are not any devices' in res.json()['detail']


####################################################### UPDATE
@pytest.mark.parametrize("additional_parameters", [
    ({}),
    ({"p1": "par1dev_test", "p2": "par2dev_test", "p3": "par3dev_test", "p4": "par4dev_test"})])
def test_device_update(authorized_client_admin, test_devices_dict, additional_parameters):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": 'Grupa_test',
        "id": test_devices_dict[0]['id']}
    device_data.update(additional_parameters)

    res = authorized_client_admin.put("/API/device_update", json=device_data)
    updated_device = schemas.Device_Response(**res.json())

    assert res.status_code == 202
    assert updated_device.name == device_data['name']


@pytest.mark.parametrize("duplicated_parametr", [
    ('name'),
    ('ip'),
    ('mac')])
def test_device_update_duplicate(authorized_client_admin, test_devices_dict, duplicated_parametr):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": 'Grupa_test',
        "id": test_devices_dict[0]['id']}

    device_data[duplicated_parametr] = test_devices_dict[1][duplicated_parametr]
    res = authorized_client_admin.put("/API/device_update", json=device_data)

    assert res.status_code == 403
    assert device_data[duplicated_parametr] in res.json()['detail']


def test_device_update_not_existing(authorized_client_admin, test_devices_dict):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": 'Grupa_test',
        "id": test_devices_dict[0]['id'] + 10}

    res = authorized_client_admin.put("/API/device_update", json=device_data)

    assert res.status_code == 404
    assert str(test_devices_dict[0]['id'] + 10) in res.json()['detail']


def test_device_update_wrong_input(authorized_client_admin, test_devices_dict):
    res = authorized_client_admin.put("/API/device_update", json=7)
    assert res.status_code == 422


####################################################### DELETE
def test_device_delete(authorized_client_admin, test_devices_dict):
    res = authorized_client_admin.delete(f"/API/device_delete?name={test_devices_dict[0]['name']}")

    assert res.status_code == 200
    assert test_devices_dict[0]['name'] in res.json()


def test_device_delete_not_existing(authorized_client_admin, test_devices_dict):
    res = authorized_client_admin.delete("/API/device_delete?name=test_device_not_exists")
    assert res.status_code == 404
    assert 'test_device_not_exists' in res.json()['detail']


def test_device_delete_wrong_input(authorized_client_admin):
    res = authorized_client_admin.delete("/API/device_delete", json=7)
    assert res.status_code == 422


####################################################### DELETE ALL
def test_device_delete_all(authorized_client_admin, test_groups_and_devices):
    group_name = test_groups_and_devices[0][0].name
    res = authorized_client_admin.delete(
        f"/API/device_delete_all?group_name={test_groups_and_devices[0][0].name}")

    assert res.status_code == 200
    assert group_name in res.json()


def test_device_delete_all_not_existing(authorized_client_admin, test_groups):
    res = authorized_client_admin.delete(f"/API/device_delete_all?group_name={test_groups[0].name}")

    assert res.status_code == 404
    assert test_groups[0].name in res.json()['detail']


####################################################### NOT LOGGED AND NOT ADMIN
def test_device_not_logged(client, test_devices_dict):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": 'Grupa_test'}

    res_device_create = client.post("/API/device_create", json=device_data)
    assert res_device_create.status_code == 401
    assert 'Not authenticated' in res_device_create.json()['detail']

    res_device_get = client.get(f"/API/device_get?name={test_devices_dict[0]['name']}")
    assert res_device_get.status_code == 401
    assert 'Not authenticated' in res_device_get.json()['detail']

    res_device_get_all = client.get("/API/device_get_all")
    assert res_device_get_all.status_code == 401
    assert 'Not authenticated' in res_device_get_all.json()['detail']

    device_data['id'] = test_devices_dict[0]['id']
    res_device_update = client.put("/API/device_update", json=device_data)
    assert res_device_update.status_code == 401
    assert 'Not authenticated' in res_device_update.json()['detail']

    res_device_delete = client.delete(f"/API/device_delete?name={test_devices_dict[0]['name']}")
    assert res_device_delete.status_code == 401
    assert 'Not authenticated' in res_device_delete.json()['detail']

    res_device_delete_all = client.delete(f"/API/device_delete_all?group_name={test_devices_dict[0]['group_name']}")
    assert res_device_delete_all.status_code == 401
    assert 'Not authenticated' in res_device_delete_all.json()['detail']


def test_group_not_admin(authorized_client, test_devices_dict):
    device_data = {
        "name": "device_test",
        "model": "model_test",
        "ob": "ob_test",
        "localization": "lokalizacja_test",
        "login": "login_test",
        "password": "password_test",
        "ip": "ip_test",
        "mask": "mask_test",
        "mac": "mac_test",
        "created_by": 'User1_test',
        "created_at": "2023-03-10 09:13",
        "group_name": 'Grupa_test'}

    res_device_create = authorized_client.post("/API/device_create", json=device_data)
    assert res_device_create.status_code == 401
    assert 'Logged user has not permission to perform that action' in res_device_create.json()['detail']

    device_data['id'] = test_devices_dict[0]['id']
    res_device_update = authorized_client.put("/API/device_update", json=device_data)
    assert res_device_update.status_code == 401
    assert 'Logged user has not permission to perform that action' in res_device_update.json()['detail']

    res_device_delete = authorized_client.delete(f"/API/device_delete?name={test_devices_dict[0]['name']}")
    assert res_device_delete.status_code == 401
    assert 'Logged user has not permission to perform that action' in res_device_delete.json()['detail']

    res_device_delete_all = authorized_client.delete(
        f"/API/device_delete_all?group_name={test_devices_dict[0]['group_name']}")
    assert res_device_delete_all.status_code == 401
    assert 'Logged user has not permission to perform that action' in res_device_delete_all.json()['detail']

