from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_EXPIRATION_TIME: int

    URL: str

    class Config:
        env_file = 'app/.env'
        #env_file = '.env'


settings = Settings()

templates = Jinja2Templates(directory="app/templates")

#import fastapi.security.oauth2 as zxc


#x = zxc.OAuth2PasswordRequestForm(username="Werka", password="q", scope='')

