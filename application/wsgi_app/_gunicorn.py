import multiprocessing
import os
from distutils.util import strtobool
from dotenv import load_dotenv

load_dotenv()

bind = f"{os.getenv('APP_DOMAIN', '127.0.0.1')}:{os.getenv('APP_PORT', '39015')}"
accesslog = '-'
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"
workers = int(os.getenv('GU_WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv('PYTHON_MAX_THREADS', 1))
reload = bool(strtobool(os.getenv('WORKER_RELOAD', 'false')))

wsgi_app = 'application.wsgi_app.app:app'