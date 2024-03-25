from fastapi import Depends, FastAPI, Request
from application.db_factory import FastAPIDatabase
from application.models import User
from .config import config

app = FastAPI()
db = FastAPIDatabase(engine_uri=config.SQLALCHEMY_DATABASE_URI)

from .controllers.auth import current_user

@app.get('/c')
def home():
    return config.__str__()

@app.get('/u')
def u(user: User = Depends(current_user)):
    return user.__repr__()

@app.get("/session")
def root(req: Request):
    return req.session