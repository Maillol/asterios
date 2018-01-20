from aiohttp import web

from .config import get_config
from .level import MetaLevel
from .models import error_middleware
from .routes import setup_routes


def main():
    """
    Read config and launch asterios server.
    """
    config = get_config()
    for level_package in config['level_package']:
        MetaLevel.load_level(level_package)

    app = web.Application(middlewares=[error_middleware])
    setup_routes(app)
    app['config'] = config
    web.run_app(app, host=config['host'], port=config['port'])


main()
