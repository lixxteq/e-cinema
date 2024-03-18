from fastapi import FastAPI, Request
from application.wsgi_app.app import app as wsgi_app
from fastapi_login import LoginManager

app = FastAPI()

@app.get("/session")
def root(req: Request):
    return req.session