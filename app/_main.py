from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def start(db: Session = Depends(get_db)):
    n = models.Group(name='Radek', created_by='Ola')
    db.add(n)
    db.commit()
    db.refresh(n)
    return 2