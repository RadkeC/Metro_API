import pytest

from app import schemas


####################################################### INIT TEST
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
@pytest.mark.parametrize("group_data", [
    ({"name": "Grupa_test_1"}),
    ({"name": "Grupa_test_2", "p1": "P_test_1", "p2": "P_test_2", "p3": "P_test_3", "p4": "P_test_4"})])
def test_group_create(authorized_client_admin, group_data):
    res = authorized_client_admin.post("/API/group_create", json=group_data)
    new_group = schemas.Group_Response(**res.json())

    assert res.status_code == 201
    assert new_group.name == group_data['name']


def test_group_create_duplicate(authorized_client_admin, test_groups):
    res = authorized_client_admin.post("/API/group_create", json={'name': test_groups[0].name})

    assert res.status_code == 403
    assert test_groups[0].name in res.json()['detail']


def test_group_create_wrong_input(authorized_client_admin):
    res = authorized_client_admin.post("/API/group_create", json=7)

    assert res.status_code == 422


####################################################### GET
@pytest.mark.parametrize("client_var, group_number, mode", [
    ('authorized_client_admin', 0, 'Group, admin'),
    ('authorized_client_admin', 1, 'Group with params, admin'),
    ('authorized_client', 0, 'Group, no admin'),
    ('authorized_client', 1, 'Group with params, no admin')])
def test_group_get(test_groups, client_var, group_number, mode, request):
    client_var = request.getfixturevalue(client_var)
    res = client_var.get(f"/API/group_get?name={test_groups[group_number].name}")
    new_group = schemas.Group_Response(**res.json())

    assert res.status_code == 200
    assert new_group.name == test_groups[group_number].name


def test_group_get_not_existing(authorized_client_admin, test_groups):
    res = authorized_client_admin.get("/API/group_get?name=test_group_not_exists")

    assert res.status_code == 404
    assert 'test_group_not_exists' in res.json()['detail']


def test_group_get_wrong_input(authorized_client_admin):
    res = authorized_client_admin.get("/API/group_get", json=7)

    assert res.status_code == 422


####################################################### GET ALL
@pytest.mark.parametrize("client_var", [
    ('authorized_client_admin'),
    ('authorized_client')])
def test_group_get_all(client_var, test_groups, request):
    client_var = request.getfixturevalue(client_var)
    res = client_var.get("/API/group_get_all")

    assert len(res.json()) == 2
    assert res.status_code == 200


def test_group_get_all_not_existing(authorized_client_admin):
    res = authorized_client_admin.get("/API/group_get_all")

    assert res.status_code == 404
    assert 'Any group does not exists' in res.json()['detail']


####################################################### UPDATE
@pytest.mark.parametrize("group_number, group_data", [
    (0, {"name": "Grupa_test_1"}),
    (1, {"name": "Grupa_test_2", "p1": "P_test_1", "p2": "P_test_2", "p3": "P_test_3", "p4": "P_test_4"}),
    (1, {"name": "Grupa_test_3", "p2": "P_test_2", "p3": "P_test_3"}),
    (0, {"name": "Grupa_test_4", "p2": "P_test_4", "p3": "P_test_4"})])
def test_group_update(authorized_client_admin, test_groups, group_number, group_data):
    group_data['id'] = test_groups[group_number].id
    res = authorized_client_admin.put("/API/group_update", json=group_data)
    updated_group = schemas.Group_Response(**res.json())

    assert res.status_code == 202
    assert updated_group.name == group_data['name']


def test_group_update_with_change_of_connected_devices(authorized_client_admin, test_groups_and_devices):
    [test_groups, test_devices] = test_groups_and_devices
    group_data = {"name": "Grupa_test_1", 'id': test_groups[0].id}
    res = authorized_client_admin.put("/API/group_update", json=group_data)
    updated_group = schemas.Group_Response(**res.json())

    assert res.status_code == 202
    assert updated_group.name == group_data['name']


def test_group_update_duplicate_name(authorized_client_admin, test_groups):
    group_data = {"name": test_groups[1].name, 'id': test_groups[0].id}
    res = authorized_client_admin.put("/API/group_update", json=group_data)

    assert res.status_code == 403
    assert test_groups[1].name in res.json()['detail']


def test_group_update_not_existing(authorized_client_admin, test_groups):
    group_data = {"name": "Grupa_test_1", 'id': test_groups[0].id + 10}
    res = authorized_client_admin.put("/API/group_update", json=group_data)

    assert res.status_code == 404
    assert f'Group with id: "{test_groups[0].id + 10}" does not exists' in res.json()['detail']


def test_group_update_wrong_input(authorized_client_admin, test_groups):
    res = authorized_client_admin.put("/API/group_update", json=7)

    assert res.status_code == 422


####################################################### DELETE
def test_group_delete(authorized_client_admin, test_groups_dict):
    res = authorized_client_admin.delete(f"/API/group_delete?name={test_groups_dict[0]['name']}")

    assert res.status_code == 200
    assert test_groups_dict[0]['name'] in res.json()


def test_group_delete_forbidden_bcs_have_devices(authorized_client_admin, test_groups_and_devices):
    groups = test_groups_and_devices[0]
    res = authorized_client_admin.delete(f"/API/group_delete?name={groups[0].name}")

    assert res.status_code == 403
    assert f'Group with name: {groups[0].name} have existing devices. ' in res.json()['detail']


def test_group_delete_not_existing(authorized_client_admin, test_groups):
    res = authorized_client_admin.delete("/API/group_delete?name=test_group_not_exists")

    assert res.status_code == 404
    assert f'Group with name: test_group_not_exists does not exists' in res.json()['detail']


def test_group_delete_wrong_input(authorized_client_admin, test_groups):
    res = authorized_client_admin.delete("/API/group_delete", json=7)

    assert res.status_code == 422


####################################################### NOT LOGGED AND NOT ADMIN
def test_group_not_logged(client, test_groups):
    group_data = {"name": "Grupa_test_1"}

    res_group_create = client.post("/API/group_create", json=group_data)
    assert res_group_create.status_code == 401
    assert 'Not authenticated' in res_group_create.json()['detail']

    res_group_get = client.get(f"/API/group_get?name={test_groups[0].name}")
    assert res_group_get.status_code == 401
    assert 'Not authenticated' in res_group_get.json()['detail']

    res_group_get_all = client.get("/API/group_get_all")
    assert res_group_get_all.status_code == 401
    assert 'Not authenticated' in res_group_get_all.json()['detail']

    group_data['id'] = test_groups[0].id
    res_group_update = client.put("/API/group_update", json=group_data)
    assert res_group_update.status_code == 401
    assert 'Not authenticated' in res_group_update.json()['detail']

    res_group_delete = client.delete(f"/API/group_delete?name={test_groups[0].name}")
    assert res_group_delete.status_code == 401
    assert 'Not authenticated' in res_group_delete.json()['detail']


def test_group_not_admin(authorized_client, test_groups):
    group_data = {"name": "Grupa_test_1"}

    res_group_create = authorized_client.post("/API/group_create", json=group_data)
    assert res_group_create.status_code == 401
    assert 'Logged user has not permission to perform that action' in res_group_create.json()['detail']

    group_data['id'] = test_groups[0].id
    res_group_update = authorized_client.put("/API/group_update", json=group_data)
    assert res_group_update.status_code == 401
    assert 'Logged user has not permission to perform that action' in res_group_update.json()['detail']

    res_group_delete = authorized_client.delete(f"/API/group_delete?name={test_groups[0].name}")
    assert res_group_delete.status_code == 401
    assert 'Logged user has not permission to perform that action' in res_group_delete.json()['detail']

