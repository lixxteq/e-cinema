from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from application.db_factory import FastAPIDatabase
from .exceptions import AuthorizationException
from application.models import User
from .config import config

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY, domain=config.SESSION_COOKIE_DOMAIN, https_only=True)
db = FastAPIDatabase(engine_uri=config.SQLALCHEMY_DATABASE_URI)

@app.exception_handler(AuthorizationException)
def authorization_exception_handler(request, exc):
    return RedirectResponse(url=config.APP_URI + '/auth/login')

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