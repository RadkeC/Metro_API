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

    class Config:
        env_file = '.env'


settings = Settings()
#print(settings)

