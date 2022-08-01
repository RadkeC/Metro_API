from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Database variables
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_NAME: str

    # JWT variables
    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_EXPIRATION_TIME: int

    # Path variables
    #URL: str

    # Hashing device's passwords variable
    PASSWORD_SECRET_KEY: str

    # Initial user variables
    INITIAL_USER_LOGIN: str
    INITIAL_USER_PASSWORD: str

    # Load variable from .env file in app folder
    class Config:
        # terminal - workdir: Metro_API - uvicorn app._main:app
        env_file = 'app/.env'
        # pycharm Run
        # env_file = '.env'

    # List of all ASCII chars on keyboard
    chars = []
    for symbol_ASCII in range(32, 127):
        chars.append(chr(symbol_ASCII))


# Handler for HTML templates folder
templates = Jinja2Templates(directory="app/templates")

# Instance of Settings class containing env variables
settings = Settings()


def hash_device_password(password, settings=settings):
    hashed_password = ''
    for letter in password:
        hashed_password = hashed_password + settings.PASSWORD_SECRET_KEY[settings.chars.index(letter)]
    return hashed_password


def unhash_device_password(hashed_password, settings=settings):
    password = ''
    for letter in hashed_password:
        password = password + settings.chars[settings.PASSWORD_SECRET_KEY.index(letter)]
    return password
