from distutils.util import strtobool
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host = os.getenv('SERVICE_DOMAIN', '127.0.0.1'),
        port = 39016,
        reload = bool(strtobool(os.getenv('WORKER_RELOAD', 'false'))),
    )