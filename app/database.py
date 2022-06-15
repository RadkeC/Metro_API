from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-addres/hostname>/<database-name>'
# postgres
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}' \
                          f'@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()






"""import psycopg2, time
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(host='localhost', database='Metro_API_Database', user='Metro_User', password='Metro_API_1120', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection was succesfull!")

except Exception as error:
    print("Connecting to database failed")
    print("Error: ", error)
    time.sleep(2)"""