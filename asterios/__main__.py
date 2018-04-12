from aiohttp import web
from aiohttp_security import setup as setup_security

from .config import get_config
from .level import MetaLevel
from .models import error_middleware
from .routes import setup_routes
from .authorization import AuthorizationPolicy, BasicAuthIdentityPolicy


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

    if config.get('authentication'):
        user_map = {
            config['authentication']['superuser']['login']: {
                'login': config['authentication']['superuser']['login'],
                'password': config['authentication']['superuser']['password'],
                'role': 'superuser'
            }
        }
        setup_security(app,
                       BasicAuthIdentityPolicy(user_map),
                       AuthorizationPolicy(user_map))

    web.run_app(app, host=config['host'], port=config['port'])


main()
