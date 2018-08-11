from json import JSONDecodeError

from aiohttp import web
from voluptuous import Invalid

from ..level import LevelSet


class ModelException(Exception):
    """
    Model base exception
    """

class ModelConflict(ModelException):
    """
    Raises when a conflict occures in the model.
    """

class DoesntExist(ModelException):
    """
    Raises when resource doesn't exist.
    """
    def __init__(self, value, field='id'):
        resource_name = type(self).__name__.replace('DoesntExist', '').lower()
        if not resource_name:
            resource_name = 'object'
        super().__init__(
            "The {resource} with {field} `{value}` doesn't exist".format(
                resource=resource_name, field=field, value=value)
        )


class GameConflict(ModelConflict):
    """
    Raises when a conflict occures.
    """

class GameDoesntExist(DoesntExist):
    """
    Raises when the expected game doesn't exist.
    """


class MemberDoesntExist(DoesntExist):
    """
    Raises when the expected team member doesn't exist.
    """


@web.middleware
async def error_middleware(request, handler):
    """
    This coroutine wraps exception in json response if an exception
    of type `Invalid`, `DoesntExist`, `ModelConflict` or
    `LevelSet.DoneException` is raised. The json response has two field
    `message` and `exception`
    """
    try:
        return await handler(request)
    except Invalid as exc:
        return web.json_response({'message': str(exc),
                                  'exception': type(exc).__qualname__},
                                 status=400)
    except DoesntExist as exc:
        return web.json_response({'message': str(exc),
                                  'exception': type(exc).__qualname__},
                                 status=404)
    except ModelConflict as exc:
        return web.json_response({'message': str(exc),
                                  'exception': type(exc).__qualname__},
                                 status=409)
    except LevelSet.DoneException as exc:
        return web.json_response({'message': 'You win!',
                                  'exception': type(exc).__qualname__},
                                 status=409)

    except JSONDecodeError as exc:
        return web.json_response({'message': str(exc),
                                  'exception': type(exc).__qualname__},
                                 status=400)

