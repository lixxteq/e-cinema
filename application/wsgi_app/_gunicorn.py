import multiprocessing
import os
from distutils.util import strtobool
from dotenv import load_dotenv

load_dotenv()

bind = os.getenv('APP_URI', '0.0.0.0:39015')
accesslog = '-'
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"
workers = int(os.getenv('GU_WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv('PYTHON_MAX_THREADS', 1))
reload = bool(strtobool(os.getenv('GU_RELOAD', 'false')))
