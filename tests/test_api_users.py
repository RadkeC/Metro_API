import pytest
from jose import jwt

from app import schemas
from app.config import settings

user_data = {
        "admin": 0,
        "name": "User_test",
        "forename": "User_test_forename",
        "department": "User_test_department",
        "login": "User_test_login",
        "password": "User_test_password"}


####################################################### INIT TEST
def test_user_init(client, test_user, test_user_admin, test_user_var):
    res = client.get("/API")
    assert res.status_code == 200
    assert test_user['login'] == 'User1_login'
    assert test_user_admin['login'] == 'User2_login' and test_user_admin['admin']
    assert test_user_var['login'] == 'User3_login'


####################################################### CREATE
def test_user_create(authorized_client):
    res = authorized_client.post("/API/user_create", json=user_data)
    new_user = schemas.User_Response(**res.json())

    assert new_user.login == user_data['login']
    assert res.status_code == 201


def test_user_create_duplicate(authorized_client, test_user_var):
    res = authorized_client.post("/API/user_create", json=test_user_var)

    assert res.status_code == 403
    assert 'already exists' in res.json()['detail']


def test_user_create_wrong_input(authorized_client):
    res = authorized_client.post("/API/user_create", json=7)
    assert res.status_code == 422


####################################################### GET
def test_user_get(authorized_client, test_user_var):
    res = authorized_client.get(f"/API/user_get?login={test_user_var['login']}")
    assert res.status_code == 200
    assert res.json()['login'] == test_user_var['login']


def test_user_get_not_existing_user(authorized_client):
    res = authorized_client.get("/API/user_get?login=test_user_not_exists")
    assert res.status_code == 404


def test_user_get_wrong_input(authorized_client):
    res = authorized_client.get("/API/user_get", json=7)
    assert res.status_code == 422


####################################################### GET ALL
def test_user_get_all(authorized_client):
    res = authorized_client.get("/API/user_get_all")
    assert len(res.json()) == 1
    assert res.status_code == 200


####################################################### UPDATE
def test_user_update(authorized_client, test_user_var):
    user_data['id'] = test_user_var['id']
    res = authorized_client.put("/API/user_update", json=user_data)
    updated_user = schemas.User_Response(**res.json())

    assert res.status_code == 202
    assert updated_user.id == user_data['id']
    assert updated_user.login == user_data['login']


def test_user_update_duplicate_login(authorized_client, test_user_var):
    user_data['id'] = test_user_var['id']
    user_data['login'] = 'User1_login'  # Login of test_user -> authorized_client
    res = authorized_client.put("/API/user_update", json=user_data)
    assert res.status_code == 403
    user_data['login'] = 'User_test_login'


def test_user_update_not_existing_user(authorized_client, test_user_var):
    user_data['id'] = test_user_var['id'] + 10
    res = authorized_client.put("/API/user_update", json=user_data)
    assert res.status_code == 404


def test_user_update_wrong_input(authorized_client):
    res = authorized_client.put("/API/user_update", json=7)
    assert res.status_code == 422


####################################################### DELETE
def test_user_delete(authorized_client, test_user_var):
    res = authorized_client.delete(f"/API/user_delete?login={test_user_var['login']}")
    assert res.status_code == 200


def test_user_delete_not_existing_user(authorized_client):
    res = authorized_client.delete("/API/user_delete?login=test_user_not_exists")
    assert res.status_code == 404


def test_user_delete_wrong_input(authorized_client):
    res = authorized_client.delete("/API/user_delete", json=7)
    assert res.status_code == 422


####################################################### NOT LOGGED
def test_user_not_logged(client, test_user_var):
    res_user_create = client.post(f"/API/user_create?login={test_user_var['login']}")
    assert res_user_create.status_code == 401

    res_user_get = client.get("/API/user_get", json={'login': test_user_var['login']})
    assert res_user_get.status_code == 401

    res_user_get_all = client.get("/API/user_get_all")
    assert res_user_get_all.status_code == 401

    user_data['id'] = test_user_var['id']
    res_user_update = client.put("/API/user_update", json=user_data)
    assert res_user_update.status_code == 401

    res_user_delete = client.delete(f"/API/user_delete?login={test_user_var['login']}")
    assert res_user_delete.status_code == 401

