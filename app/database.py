from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-addres/hostname>/<database-name>'
# Postgres db url handler
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}' \
                          f'@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}'

# Creating connection to db
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency function for paths
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
