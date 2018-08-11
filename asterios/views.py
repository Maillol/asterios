from datetime import datetime
import json
from json.decoder import JSONDecodeError

from aiohttp import web
from aiohttp_security import has_permission

from .level import LevelSet, Difficulty
from .models import TeamMember, Game
from .models.basemodel import Collection


class JSONEncoder(json.JSONEncoder):
    """
    This JSONEncoder can encode datetime using ISO 8601 format
    and LevelSet object to dict with `theme` and `level` keys.
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, LevelSet):
            return {'theme': o.theme,
                    'level': o.level_number}
        if isinstance(o, Difficulty):
            return o.value
        if isinstance(o, TeamMember):
            return {'id': o.id,
                    'name': o.name,
                    'level': o.level,
                    'level_max': o.level_max,
                    'theme': o.theme,
                    'difficulty': o.difficulty,
                    'levels_obj': o.levels_obj,
                    'won_at': o.won_at}
        if isinstance(o, Collection):
            return list(o)
        if isinstance(o, Game):
            ret = {
                'team': o.team,
                'state': o.state,
                'duration': o.duration,
                'team_members': o.team_members}

            if o.start_at is not None:
                ret['start_at'] = o.start_at

            if o.remaining is not None:
                ret['remaining'] = o.remaining

            return ret
        return json.JSONEncoder.default(self, o)


def json_response(obj, status=200):
    return web.json_response(obj, status=status,
                             dumps=JSONEncoder().encode)


class GameConfigView:
    """
    Create a game configuration and start it.
    """

    async def get(self, request):
        """
        .. http:get:: /game-config/(str:name)

           Return a created game configuration selected by `name`.

           :statuscode 200: If the game is found
           :statuscode 404: If the game doesn't exist

           **Example request**:

           .. sourcecode:: http

              GET /game-config/team-17 HTTP/1.1
              Host: example.com

           **Example response**:

           .. sourcecode:: http

              HTTP/1.1 200 Ok
              Content-Type: application/json

              {
                "team": "team-17",
                "team_members": [{
                  "name": "Toto",
                  "id": 2013,
                  "levels_obj": {
                    "level": 2,
                    "theme": "laby"
                  },
                  "level": 1,
                  "level_max": 2
                }],
                "state": "start",
                "start_at": "2018-01-21T15:42:44.711888",
                "duration": 10,
                "remaining": 10
              }

           :<json str team: The name of team
           :<json list teams_members: The list of teams member
           :<json str teams_members[].id: (generated) The id of teams member
           :<json str teams_members[].name: The name of teams member
           :<json int teams_members[].level: The start level chosen by
               the team member
           :<json int teams_members[].theme: The theme of puzzle chosen by
               the team member
           :<json int teams_members[].level_max: The last level
           :<json int teams_members[].level_obj.level: (generated) The
               current level
           :<json int teams_members[].level_obj.theme: (generated) The
               current theme
           :<json str state: (generated) The state of game
           :<json str start_at: (generated) The starting date
           :<json int duration: The game duration in minute
           :<json int remaining: (generated) The remaining time in minute
           :<json int won_at: (generated,optional) The date of victory in
               ISO 8601 format

        """
        name = request.match_info.get('name')
        if name is None:
            result = request.app['model'].games()
        else:
            result = request.app['model'].game(name)
        return json_response(result)

    async def post(self, request):
        """
        .. http:post:: /game-config

           Create a game configuration.

           :statuscode 201: Created
           :statuscode 409: If The game config already exist

           **Example request**:

           .. sourcecode:: http

              POST /game-config HTTP/1.1
              Host: example.com
              Content-Type: application/json

              {
                "team": "team-17",
                "team_members": [{
                  "name": "Toto"
                }],
                "duration": 10
              }

           :>json str team: The name of team
           :>json int duration: The game duration in minute
           :>json list teams_members: The list of teams member
           :>json str teams_members[].name: The name of the team member
           :>json str teams_members[].theme: (optional) The theme of puzzle
               set. Chosen randomly if not set.
           :>json str teams_members[].difficulty: (optional) The difficulty of
               puzzle set. Expected value: "easy", "normal" or "hard".
           :>json int teams_members[].level: (optional) The starting level
           :>json int teams_members[].level_max: (optional) The last level.

           **Example response**:

           .. sourcecode:: http

              HTTP/1.1 201 Created
              Content-Type: application/json

              {
                "team": "team-17",
                "team_members": [{
                  "name": "Toto",
                  "id": 2013,
                  "levels_obj": {
                    "level": 2,
                    "theme": "laby"
                  },
                  "level": 1,
                  "level_max": 2
                }],
                "duration": 10,
                "state": "ready"
              }

           :<json str team: The name of team
           :<json list teams_members: The list of teams member
           :<json str teams_members[].id: (generated) The id of teams member
           :<json str teams_members[].name: The name of teams member
           :<json int teams_members[].level: The start level chosen by
               the team member
           :<json int teams_members[].theme: The theme of puzzle chosen by
               the team member
           :<json str teams_members[].difficulty: The difficulty of
               puzzle set chosen by the team member.
           :<json int teams_members[].level_max: The last level
           :<json int teams_members[].level_obj.level: (generated) The
               current level
           :<json int teams_members[].level_obj.theme: (generated) The
               current theme
           :<json str state: (generated) The state of game
           :<json str start_at: (generated) The starting date
           :<json int duration: The game duration in minute
           :<json int remaining: (generated) The remaining time in minute
           :<json int won_at: (generated,optional) The date of victory in
               ISO 8601 format

        """
        try:
            game_config = await request.json()
        except JSONDecodeError as error:
            return json_response(str(error), status=400)
        game = request.app['model'].create(game_config)
        return json_response(game, status=201)

    @has_permission('gameconfig.delete')
    async def delete(self, request):
        """
        .. http:delete:: /game-config/(str:name)

           Delete a game configuration

           .. sourcecode:: http

              DELETE /game-config/team-17 HTTP/1.1
              Host: example.com
              Content-Type: application/json
        """
        name = request.match_info.get('name')
        request.app['model'].delete_game(name)
        return json_response({})

    async def put(self, request):
        """
        .. http:put:: /game-config/(str:name)/(str:action)

           Action `start` - start a created game configuration selected by `name`.

           :statuscode 200: If the game is started
           :statuscode 404: If the game doesn't exist
           :statuscode 409: If the game is already started

           **Example request**:

           .. sourcecode:: http

              PUT /game-config/team-17/start HTTP/1.1
              Host: example.com
              Content-Type: application/json

              {
                "name": "Toto",
                "difficulty": "easy"
              }

             :>json str name: The name of the team member
             :>json str theme: (optional) The theme of puzzle
                 set. Chosen randomly if not set.
             :>json str difficulty: (optional) The difficulty of
                 puzzle set. Expected value: "easy", "normal" or "hard".
             :>json int level: (optional) The starting level
             :>json int level_max: (optional) The last level.

             **Example response**:

           .. sourcecode:: http

              HTTP/1.1 200 Ok
              Content-Type: application/json

              {
                "team": "team-17",
                "team_members": [{
                  "name": "Toto",
                  "id": 2013,
                  "levels_obj": {
                    "level": 2,
                    "theme": "laby"
                  },
                  "level": 1,
                  "level_max": 2
                }],
                "state": "start",
                "start_at": "2018-01-21T15:42:44.711888",
                "duration": 10,
                "remaining": 10
              }

           :<json str team: The name of team
           :<json list teams_members: The list of teams member
           :<json str teams_members[].id: (generated) The id of teams member
           :<json str teams_members[].name: The name of teams member
           :<json int teams_members[].level: The start level chosen by
               the team member
           :<json int teams_members[].theme: The theme of puzzle chosen by
               the team member
           :<json str teams_members[].difficulty: The difficulty of
               puzzle set chosen by the team member.
           :<json int teams_members[].level_max: The last level
           :<json int teams_members[].level_obj.level: (generated) The
               current level
           :<json int teams_members[].level_obj.theme: (generated) The
               current theme
           :<json str state: (generated) The state of game
           :<json str start_at: (generated) The starting date
           :<json int duration: The game duration in minute
           :<json int remaining: (generated) The remaining time in minute
           :<json int won_at: (generated,optional) The date of victory in
               ISO 8601 format

           Action `add-member` - Add a new member to the game.

           :statuscode 200: If add-member is added
           :statuscode 404: If the game doesn't exist
           :statuscode 409: If the game is already started
        """

        action = request.match_info.get('action')
        name = request.match_info.get('name')
        game = request.app['model'].game(name)

        if action == 'start':
            game.start()
            return json_response(game)

        elif action == 'add-member':
            game.add_member(await request.json())
            return json_response(game)

        else:
            return json_response(
                {'message': 'Game has no action `{}`'.format(action),
                 'exception': 'HasNoActionError'},
                status=405)


class AsteriosView:

    @staticmethod
    async def get(request):
        """
        .. http:get:: /asterios/(str:team)/member/(str:team_member)

           Return a member of team.

           :statuscode 200: If the team member is found
           :statuscode 404: If the team member doesn't exist

           **Example request**:

           .. sourcecode:: http

              GET /asterios/(str:team)/member/(str:team_member) HTTP/1.1
              Host: example.com

           **Example response**:

           .. sourcecode:: http

              HTTP/1.1 200 Ok
              Content-Type: application/json

                {
                  "name": "Toto",
                  "id": 2013,
                  "levels_obj": {
                    "level": 2,
                    "theme": "laby"
                  },
                  "level": 1,
                  "level_max": 2
                }

           :<json str id: (generated) The id of teams member
           :<json str name: The name of teams member
           :<json int level: The start level chosen by
               the team member
           :<json int theme: The theme of puzzle chosen by
               the team member
           :<json int level_max: The last level
           :<json int level_obj.level: (generated) The
               current level
           :<json int level_obj.theme: (generated) The
               current theme
        """

        team = request.match_info.get('team')
        member_id = request.match_info.get('member')
        return json_response(member_from_id(team, member_id))

    @staticmethod
    async def post(request):
        raise web.HTTPMethodNotAllowed()

    @staticmethod
    async def delete(request):
        raise web.HTTPMethodNotAllowed()

    @staticmethod
    async def put(request):
        """
        .. http:put:: /asterios/(str:team)/member/(str:team_member)/(str:action)

           Action `puzzle` - Get puzzle of current level. A new puzzle is
           generated for each request.

           :statuscode 200: Question is generated and returned
           :statuscode 404: If the game or team member doesn't exist

           **Example request**:

           .. sourcecode:: http

              GET /asterios/team-17/member/2013/puzzle HTTP/1.1
              Host: example.com

           **Example response**:

           .. sourcecode:: http

              HTTP/1.1 200 Ok
              Content-Type: application/json

              {
                "puzzle": ["lmn", "fhj", "jih"],
                "tip":  "ace -> g"
              }

           :<json any puzzle: The puzzle to solve
           :<json str tip: A short help to solve the puzzle

           Action `solve` - Try to solve the puzzle.

           :statuscode 200: The puzzle is solved.
           :statuscode 404: If the game or team member doesn't exist

                       420 – The puzzle isn't solved.


           **Example request**:

           .. sourcecode:: http

              GET /asterios/team-17/member/2013/solve HTTP/1.1
              Host: example.com

           **Example response**:

           .. sourcecode:: http

              HTTP/1.1 200 Ok
              Content-Type: application/json

              ["o", "l", "g"]
        """
        team = request.match_info.get('team')
        member_id = request.match_info.get('member')
        action = request.match_info.get('action')

        if action == 'puzzle':
             return json_response(
                request.app['model'].set_question(team, member_id))

        elif action == 'solve':
            try:
                answer = await request.json()
            except JSONDecodeError as error:
                return json_response(str(error), status=400)

            is_exact, comment = request.app['model'].check_answer(team, member_id, answer)
            if is_exact:
                return json_response(comment, status=201)
            return json_response(comment, status=420)

        return json_response(
            {'message': 'TeamMember has no action `{}`'.format(action),
             'exception': 'HasNoActionError'},
            status=405)

