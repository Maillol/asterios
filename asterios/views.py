from datetime import datetime
import json
from json.decoder import JSONDecodeError

from aiohttp import web

from .level import LevelSet
from .models import GAMES


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, LevelSet):
            return {'theme': o.theme,
                    'level': o.level_number}
        return json.JSONEncoder.default(self, o)


def json_response(obj, status=200):
    return web.json_response(obj, status=status,
                             dumps=JSONEncoder().encode)


class GameConfig(web.View):
    """
    Create a game configuration and start it.
    """

    async def get(self):
        """
        .. http:get:: /game-config/(str:name)

            Start a created game configuration selected by `name`.

            **Example request**:

            .. sourcecode:: http

               GET /game-config/team-17 HTTP/1.1
               Host: example.com

            **Example response**:

            .. sourcecode:: http

               HTTP/1.1 200 Ok

               {
                 "team": "team-17",
                 "team_members": [{
                   "name": "Toto",
                   "id": 2013,
                   "levels_obj": null,
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
            :<json int teams_members[].level: (optional) The current level
            :<json int teams_members[].level_max: (optional) The last level
            :<json str state: (generated) The state of game
            :<json str start_at: (generated) The starting date
            :<json int duration: The game duration in minute
            :<json int remaining: (generated) The remaining time in minute

            :statuscode 200: If the game is found
            :statuscode 404: If the game doesn't exist
        """
        name = self.request.match_info.get('name')
        if name is None:
            return json_response(list(GAMES))

        game = GAMES.get(name)
        return json_response(game)

    async def post(self):
        """
        .. http:post:: /game-config

            Create a game configuration.

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
            :>json str teams_members[].name: The name of teams member
            :>json int teams_members[].level: (optional) The starting level
            :>json int teams_members[].level_max: (optional) The last level.

            **Example response**:

            .. sourcecode:: http

               HTTP/1.1 201 Created

               {
                 "team": "team-17",
                 "team_members": [{
                   "name": "Toto",
                   "id": 2013,
                   "levels_obj": null,
                   "level": 1,
                   "level_max": 2
                 }],
                 "duration": 10,
                 "state": "ready"
               }

            :<json str team: The name of team
            :<json int duration: The game duration in minute
            :<json list teams_members: The list of teams member
            :<json str teams_members[].id: (generated) The id of teams member
            :<json str teams_members[].name: The name of teams member
            :<json int teams_members[].level: (optional) The starting level
            :<json int teams_members[].level_max: (optional) The last level.
            :<json str state: (generated) The state of game.

            :statuscode 201: Created
            :statuscode 409: If The game config already exist
        """
        try:
            game_config = await self.request.json()
        except JSONDecodeError as error:
            return json_response(str(error), status=400)
        game = GAMES.create(game_config['team'], game_config)
        return json_response(game, status=201)

    async def delete(self):
        """
        TODO
        """
        name = self.request.match_info.get('name')
        GAMES.delete(name)
        return json_response({})

    async def put(self):
        """
        .. http:put:: /game-config/(str:name)

            Start a created game configuration selected by `name`.

            **Example request**:

            .. sourcecode:: http

               PUT /game-config/team-17 HTTP/1.1
               Host: example.com

            **Example response**:

            .. sourcecode:: http

               HTTP/1.1 200 Ok

               {
                 "team": "team-17",
                 "team_members": [{
                   "name": "Toto",
                   "id": 2013,
                   "levels_obj": null,
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
            :<json int teams_members[].level: (optional) The current level
            :<json int teams_members[].level_max: (optional) The last level
            :<json str state: (generated) The state of game
            :<json str start_at: (generated) The starting date
            :<json int duration: The game duration in minute
            :<json int remaining: (generated) The remaining time in minute

            :statuscode 200: If the game is started
            :statuscode 404: If the game doesn't exist
            :statuscode 409: If the game is already started
        """
        name = self.request.match_info.get('name')
        game = GAMES.start(name)
        return json_response(game)


class AsteriosView(web.View):

    async def get(self):
        """
        .. http:get:: /game-config/(str:name)

            Get puzzle of current level. A new puzzle is generated for each
            request.

            **Example request**:

            .. sourcecode:: http

               GET /asterios/team-17/member/2013 HTTP/1.1
               Host: example.com

            **Example response**:

            .. sourcecode:: http

               HTTP/1.1 200 Ok

               {
                 "puzzle": ["lmn", "fhj", "jih"],
                 "tip":  "ace -> g"
               }

            :<json any puzzle: The puzzle to solve
            :<json str tip: A short help to solve the puzzle

            :statuscode 200: Question is generated and returned
            :statuscode 404: If the game or team member doesn't exist
        """
        team = self.request.match_info.get('team')
        member = self.request.match_info.get('member')
        return json_response(GAMES.set_question(team, member))

    async def post(self):
        """
        .. http:get:: /game-config/(str:name)

            Send a solved puzzle.

            **Example request**:

            .. sourcecode:: http

               GET /asterios/team-17/member/2013 HTTP/1.1
               Host: example.com

            **Example response**:

            .. sourcecode:: http

               HTTP/1.1 200 Ok

               ["o", "l", "g"]

            :statuscode 200: The puzzle is solved.
            :statuscode 404: If the game or team member doesn't exist

                        420 – The puzzle isn't solved.
        """
        try:
            answer = await self.request.json()
        except JSONDecodeError as error:
            return json_response(str(error), status=400)

        team = self.request.match_info.get('team')
        member = self.request.match_info.get('member')

        is_exact, comment = GAMES.check_answer(team, member, answer)
        if is_exact:
            return json_response(comment, status=201)
        return json_response(comment, status=420)
