from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app._main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models, schemas

# CREATING DB FOR TESTS
# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-addres/hostname>/<database-name>'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}' \
                          f'@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}_test'

print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
connection = engine.connect()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sess = TestingSessionLocal()


# SESSION FIXTURE
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Client FIXTURE
@pytest.fixture()
def client(session):
    def override_get_db():

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    print('yeld app')
    yield TestClient(app)


# USER FIXTURE
@pytest.fixture
def test_user(client, session):
    user_data = {
        "admin": 0,
        "name": "User1_name",
        "forename": "User1_forename",
        "department": "User1_department",
        "login": "User1_login",
        "password": "User1_password",
        "created_by": "User1_creator",
        "created_at": "2023-03-10 09:13"}

    new_user = models.User(**user_data)
    session.add(new_user)
    session.commit()

    res = session.query(models.User).filter(models.User.login == user_data['login']).first()
    assert res.login == user_data['login']

    user_data['id'] = res.id
    return user_data


@pytest.fixture
def test_user_admin(client, session):
    user_data = {
        "admin": 1,
        "name": "User2_name",
        "forename": "User2_forename",
        "department": "User2_department",
        "login": "User2_login",
        "password": "User2_password",
        "created_by": "User2_creator",
        "created_at": "2023-03-10 09:13"}

    new_user = models.User(**user_data)
    session.add(new_user)
    session.commit()

    res = session.query(models.User).filter(models.User.login == user_data['login']).first()
    assert res.login == user_data['login']

    user_data['id'] = res.id
    return user_data


@pytest.fixture
def test_user_var(client, session):
    user_data = {
        "admin": 0,
        "name": "User3_name",
        "forename": "User3_forename",
        "department": "User3_department",
        "login": "User3_login",
        "password": "User3_password",
        "created_by": "User3_creator",
        "created_at": "2023-03-10 09:13"}

    new_user = models.User(**user_data)
    session.add(new_user)
    session.commit()

    res = session.query(models.User).filter(models.User.login == user_data['login']).first()
    assert res.login == user_data['login']

    user_data['id'] = res.id
    return user_data


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def token_admin(test_user_admin):
    return create_access_token({"user_id": test_user_admin['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def authorized_client_admin(client, token_admin):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token_admin}"
    }

    return client


@pytest.fixture
def test_groups(test_user_admin, session):
    groups_data = [{
        "name": "Grupa 1",
        "created_by": test_user_admin['login'],
        "created_at": "2023-03-10 09:13"},
        {
        "name": "Grupa 2",
        "created_by": test_user_admin['login'],
        "created_at": "2023-03-10 09:13",
        "p1": "Parametr 1",
        "p2": "Parametr 2",
        "p3": "Parametr 3",
        "p4": "Parametr 4"}]

    def create_group_model(group):
        return models.Group(**group)

    group_map = map(create_group_model, groups_data)
    groups = list(group_map)

    session.add_all(groups)
    session.commit()

    groups = session.query(models.Group).all()
    return groups


@pytest.fixture
def test_groups_and_devices(test_user_admin, session):
    #groups = test_groups
    groups = [{'name': 'Grupa 1'}, {'name': 'Grupa 2'}]
    devices_data = [
        {
            "name": "device 1",
            "model": "model 1",
            "ob": "ob 1",
            "localization": "lokalizacja 1",
            "login": "login 1",
            "password": "password1",
            "ip": "ip1",
            "mask": "mask1",
            "mac": "mac1",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[0]['name']
        },
        {
            "name": "device 2",
            "model": "model 1",
            "ob": "ob 2",
            "localization": "lokalizacja 1",
            "login": "login 2",
            "password": "password2",
            "ip": "ip2",
            "mask": "mask2",
            "mac": "mac2",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[0]['name']
        },
        {
            "name": "device 3",
            "model": "model 2",
            "ob": "ob 1",
            "localization": "lokalizacja 1",
            "login": "login 3",
            "password": "password3",
            "ip": "ip3",
            "mask": "mask3",
            "mac": "mac3",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[1]['name'],
            "p1": "par1dev3",
            "p2": "par2dev3",
            "p3": "par3dev3",
            "p4": "par4dev3"
        },
        {
            "name": "device 4",
            "model": "model 2",
            "ob": "ob 2",
            "localization": "lokalizacja 1",
            "login": "login 4",
            "password": "password4",
            "ip": "ip4",
            "mask": "mask4",
            "mac": "mac4",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[1]['name'],
            "p1": "par1dev4",
            "p2": "par2dev4",
            "p3": "par3dev4",
            "p4": "par4dev4"
        }]

    def create_device_model(device):
        return models.Device(**device)

    device_map = map(create_device_model, devices_data)
    devices = list(device_map)

    session.add_all(devices)
    session.commit()

    devices = session.query(models.Device).all()

    groups_data = [{
        "name": "Grupa 1",
        "created_by": test_user_admin['login'],
        "created_at": "2023-03-10 09:13"},
        {
            "name": "Grupa 2",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "p1": "Parametr 1",
            "p2": "Parametr 2",
            "p3": "Parametr 3",
            "p4": "Parametr 4"}]

    def create_group_model(group):
        return models.Group(**group)

    group_map = map(create_group_model, groups_data)
    groups = list(group_map)

    session.add_all(groups)
    session.commit()

    groups = session.query(models.Group).all()

    return [groups, devices]


@pytest.fixture
def test_groups_dict(test_user_admin, session):
    groups_data = [{
        "name": "Grupa 1",
        "created_by": test_user_admin['login'],
        "created_at": "2023-03-10 09:13"},
        {
        "name": "Grupa 2",
        "created_by": test_user_admin['login'],
        "created_at": "2023-03-10 09:13",
        "p1": "Parametr 1",
        "p2": "Parametr 2",
        "p3": "Parametr 3",
        "p4": "Parametr 4"}]

    def create_group_model(group):
        return models.Group(**group)

    group_map = map(create_group_model, groups_data)
    groups = list(group_map)

    session.add_all(groups)
    session.commit()

    groups = session.query(models.Group).all()
    for number in range(2):
        groups_data[number]['id'] = groups[number].id
    return groups_data


@pytest.fixture
def test_devices_dict(test_user_admin, session):
    groups = [{'name': 'Grupa 1'}, {'name': 'Grupa 2'}]
    devices_data = [
        {
            "name": "device 1",
            "model": "model 1",
            "ob": "ob 1",
            "localization": "lokalizacja 1",
            "login": "login 1",
            "password": "password1",
            "ip": "ip1",
            "mask": "mask1",
            "mac": "mac1",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[0]['name']
        },
        {
            "name": "device 2",
            "model": "model 1",
            "ob": "ob 2",
            "localization": "lokalizacja 1",
            "login": "login 2",
            "password": "password2",
            "ip": "ip2",
            "mask": "mask2",
            "mac": "mac2",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[0]['name']
        },
        {
            "name": "device 3",
            "model": "model 2",
            "ob": "ob 1",
            "localization": "lokalizacja 1",
            "login": "login 3",
            "password": "password3",
            "ip": "ip3",
            "mask": "mask3",
            "mac": "mac3",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[1]['name'],
            "p1": "par1dev3",
            "p2": "par2dev3",
            "p3": "par3dev3",
            "p4": "par4dev3"
        },
        {
            "name": "device 4",
            "model": "model 2",
            "ob": "ob 2",
            "localization": "lokalizacja 1",
            "login": "login 4",
            "password": "password4",
            "ip": "ip4",
            "mask": "mask4",
            "mac": "mac4",
            "created_by": test_user_admin['login'],
            "created_at": "2023-03-10 09:13",
            "group_name": groups[1]['name'],
            "p1": "par1dev4",
            "p2": "par2dev4",
            "p3": "par3dev4",
            "p4": "par4dev4"
        }]

    def create_device_model(device):
        return models.Device(**device)

    device_map = map(create_device_model, devices_data)
    devices = list(device_map)

    session.add_all(devices)
    session.commit()

    devices = session.query(models.Device).all()

    for number in range(4):
        devices_data[number]['id'] = devices[number].id

    return devices_data
