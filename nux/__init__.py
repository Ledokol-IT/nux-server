import uvicorn

from nux.app import create_app
from nux.config import options


def run_app():
    uvicorn.run(create_app(), port=options.port, host="0.0.0.0")
