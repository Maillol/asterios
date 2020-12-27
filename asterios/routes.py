"""
This module contains code to bind http handers to a http route.
"""

from aiohttp import web
from aiohttp.web_routedef import AbstractRouteDef
import attr

from .views import AsteriosView, GameConfigView


@attr.s(frozen=True, repr=False, slots=True)
class _ClassHandlerRouteDef(AbstractRouteDef):
    """
    Register coroutines of a class as http handler in a router.

    The class_handler should define get, put, delete and post coroutine.
    The route below will be created:

    POST /{prefix_path}                         Create resource
    GET  /{prefix_path}                         Select all resources
    DELETE /{prefix_path}/{{key_name}}          Delete a resource
    GET /{prefix_path}/{{key_name}}             Select a resource
    PUT /{prefix_path}/{{key_name}}/{action}    Apply action on resource
    """

    prefix_path = attr.ib(type=str)
    class_handler = attr.ib()
    key_name = attr.ib(type=str)
    suffix_name = attr.ib(type=str)

    @staticmethod
    def build_not_allowed_handler(method, allowed_methods):
        """
        Build a HTTP handler returning Not Allowed error
        """

        async def not_allowed(request):  # pylint: disable=unused-argument
            """
            This handler is used when a class not implement a http handler
            """
            raise web.HTTPMethodNotAllowed(
                method=method, allowed_methods=allowed_methods)

        return not_allowed

    def register(self, router):
        """
        Register all http handler defined in `class_handler`.
        """
        handlers = self.class_handler()
        suffix = self.suffix_name
        path = self.prefix_path

        allowed_methods = [
            method for method in ('get', 'post', 'delete', 'get', 'put')
            if hasattr(handlers, 'method')]

        def get_hander(mtd_name):
            """Return handler of `class_handler` or not_allowed handler."""
            return getattr(
                handlers,
                mtd_name.lower(),
                self.build_not_allowed_handler(mtd_name.upper(), allowed_methods))

        handler = get_hander('post')
        router.add_route('POST', path, handler, name='create-' + suffix)
        handler = get_hander('get')
        router.add_route('GET', path, handler, name='list-' + suffix)

        path = '{}/{{{}}}'.format(self.prefix_path, self.key_name)
        handler = get_hander('delete')
        router.add_route('DELETE', path, handler, name='delete-' + suffix)
        handler = get_hander('get')
        router.add_route('GET', path, handler, name='get-' + suffix)

        path = '{}/{{{}}}/{{action}}'.format(self.prefix_path, self.key_name)
        handler = get_hander('put')
        router.add_route('PUT', path, handler, name='action-' + suffix)


def route(prefix_path, class_handler, key_name, suffix_name):
    """
    route handlers defined in a class using a _ClassHandlerRouteDef.
    """
    return _ClassHandlerRouteDef(
        prefix_path, class_handler, key_name, suffix_name)


def setup_routes(app):
    """
    Bind all asterios view with a route.
    """
    app.router.add_routes([
        route('/game-config',
              GameConfigView, key_name='name', suffix_name='game'),
        route('/asterios/{team}/member',
              AsteriosView, key_name='member', suffix_name='asterios'),
    ])
