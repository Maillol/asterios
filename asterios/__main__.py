from aiohttp import web
import sys
from . import make_app


app = make_app(sys.argv[1:])
web.run_app(app,
            host=app['config']['host'],
            port=app['config']['port'])
