from typing import Optional, List

from aiohttp import web
from aiohttp_pydantic import oas
from aiohttp_security import setup as setup_security

from .config import get_config
from .level import MetaLevel
from .models import error_middleware, Model
from .routes import setup_routes
from .authorization import AuthorizationPolicy, BasicAuthIdentityPolicy


__version__ = "2.1.2"


def make_app(config_args: Optional[List] = None):
    """
    Read config and launch asterios server.
    """
    config = get_config(config_args)
    for level_package in config["level_package"]:
        MetaLevel.load_level(level_package)
    MetaLevel.load_installed_levels()

    app = web.Application(middlewares=[error_middleware])
    setup_routes(app)
    app["config"] = config
    app["model"] = Model()

    if config.get("authentication"):
        user_map = {
            config["authentication"]["superuser"]["login"]: {
                "login": config["authentication"]["superuser"]["login"],
                "password": config["authentication"]["superuser"]["password"],
                "role": "superuser",
            }
        }
        setup_security(
            app, BasicAuthIdentityPolicy(user_map), AuthorizationPolicy(user_map)
        )

    oas.setup(app)
    return app
