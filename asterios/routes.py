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

    def register(self, router):
        handlers = self.class_handler()
        suffix = self.suffix_name

        path = self.prefix_path
        router.add_route('POST', path, handlers.post, name='create-' + suffix)
        router.add_route('GET', path, handlers.get, name='list-' + suffix)

        path = '{}/{{{}}}'.format(self.prefix_path, self.key_name)
        router.add_route('DELETE', path, handlers.delete, name='delete-' + suffix)
        router.add_route('GET', path, handlers.get, name='get-' + suffix)

        path = '{}/{{{}}}/{{action}}'.format(self.prefix_path, self.key_name)
        router.add_route('PUT', path, handlers.put, name='action-' + suffix)


def route(prefix_path, class_handler, key_name, suffix_name):
    return _ClassHandlerRouteDef(prefix_path, class_handler, key_name, suffix_name)


def setup_routes(app):
    app.router.add_routes([
        route('/game-config',
              GameConfigView, key_name='name', suffix_name='game'),
        route('/asterios/{team}/member',
              AsteriosView, key_name='member', suffix_name='asterios'),
    ])

