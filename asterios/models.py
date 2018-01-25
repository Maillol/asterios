from datetime import datetime
import itertools
import random

from aiohttp import web
from voluptuous import (REMOVE_EXTRA, All, Any, Invalid, Length, Range, Remove,
                        Required, Schema)

from .level import BaseLevel, get_level_set, get_themes, LevelSet


class GameException(Exception):
    """
    Game base exception raised by the Games class.
    """


class GameConflict(GameException):
    """
    Raises when a conflict occures.
    """


class DoesntExist(GameException):
    """
    Raises when resource doesn't exist.
    """


class GameDoesntExist(DoesntExist):
    """
    Raises when the expected game doesn't exist.
    """

    def __init__(self, name):
        super().__init__("The game with name `{name}` doesn't exist".
                         format(name=name))


class MemberDoesntExist(DoesntExist):
    def __init__(self, name, field='name'):
        super().__init__("The member with {field} `{name}` doesn't exist".
                         format(**locals()))


def utcnow():
    """
    Mock me ;-)
    """
    return datetime.utcnow()


class Games:

    @staticmethod
    def _set_remaining_time(game):
        now = utcnow()
        if game['state'] == 'start':
            consumption = (now - game['start_at']).seconds // 60
            game['remaining'] = max(game['duration'] - consumption, 0)
            if game['remaining'] == 0:
                game['state'] = 'stop'

    def __init__(self):
        self._games = {}

    def create(self, name, game):
        game = create_game_validator(game)
        if name in self._games:
            raise GameConflict(
                'The game with name `{name}` already exists'.
                format(**locals()))

        themes_iterator = itertools.cycle(get_themes())
        for user in game['team_members']:
            user['id'] = random.randint(1000, 9999)
            user['levels_obj'] = get_level_set(next(themes_iterator),
                                               user['level'],
                                               user['level_max'])
        self._games[name] = game
        return game

    def get(self, name):
        if name not in self._games:
            raise GameDoesntExist(name)
        game = self._games[name]
        self._set_remaining_time(game)
        return game

    def __iter__(self):
        for game in self._games.values():
            self._set_remaining_time(game)
            yield game

    def delete(self, name):
        if name not in self._games:
            raise GameDoesntExist(name)
        del self._games[name]

    def start(self, name):
        game = self.get(name)
        if game['state'] == 'start':
            raise GameConflict(
                'The game `{name}` is already started'.format(**locals()))

        game['state'] = 'start'
        game['start_at'] = utcnow()
        game['remaining'] = game['duration']
        return game

    def drop(self):
        self._games.clear()

    def set_question(self, game_name, member_id):
        member = self.member_from_id(game_name, member_id)
        level_set = member['levels_obj']
        return {
            'puzzle': level_set.generate_puzzle(),
            'tip': level_set.tip(),
        }

    def check_answer(self, game_name, member_id, answer):
        game = self.get(game_name)
        if game['state'] != 'start':
            raise GameConflict(
                'The game `{game_name}` is not started'.format(**locals()))

        member = self.member_from_id(game_name, member_id)
        level_set = member['levels_obj']
        is_exact, comment = level_set.check_answer(answer)
        if is_exact:
            if level_set.done:
                member['win_at'] = utcnow()
            else:
                member['level'] = level_set.level_number
                self.set_question(game_name, member_id)
        return is_exact, comment

    def member_from_id(self, game_name, member_id):
        try:
            member_id = int(member_id)
        except ValueError:
            raise MemberDoesntExist(member_id, field='id')

        game = self.get(game_name)
        member = next((member for member
                       in game['team_members']
                       if member['id'] == member_id), None)

        if member is None:
            raise MemberDoesntExist(member_id, field='id')
        return member

    def member_from_name(self, game_name, member_name):
        game = self.get(game_name)
        member = next((member for member
                       in game['team_members']
                       if member['name'] == member_name), None)

        if member is None:
            raise MemberDoesntExist(member_name)
        return member


GAMES = Games()

create_game_validator = Schema({
    Required('team'): str,
    Required('team_members'): All([
        {
            Required('name'): str,
            Required('level', default=1): All(int, Range(min=1)),
            Required('skill', default=''): str,
            Required('level_max', default=2): All(int, Range(min=1)),
        }
    ], Length(min=1)),
    Required('state', default='ready'): 'ready',
    Required('duration'): All(int, Range(min=1)),
})


get_game_validator = Schema({
    Required('team'): str,
    Required('team_members'): All([
        {
            Required('name'): str,
            Required('level'): All(int, Range(min=1)),
            Required('skill'): str,
            Required('id'): str,
            Required('level_max'): All(int, Range(min=1)),
            Remove('levels_obj'): BaseLevel
        }
    ], Length(min=1)),
    Required('state'): Any('ready', 'start', 'stop',
                           msg='Expected ready, start or stop'),
    Required('duration'): All(int, Range(min=1)),
    Required('remaining'): int
}, extra=REMOVE_EXTRA)


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except Invalid as exc:
        return web.json_response({'message': str(exc)},
                                 status=400)
    except DoesntExist as exc:
        return web.json_response({'message': str(exc)},
                                 status=404)
    except GameConflict as exc:
        return web.json_response({'message': str(exc)},
                                 status=409)
    except LevelSet.DoneException:
        return web.json_response({'message': 'You win!'},
                                 status=409)
