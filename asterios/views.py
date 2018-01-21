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
            return None
        return json.JSONEncoder.default(self, o)


def json_response(obj, status=200):
    return web.json_response(obj, status=status,
                             dumps=JSONEncoder().encode)


class GameConfig(web.View):

    async def get(self):
        name = self.request.match_info.get('name')
        if name is None:
            return json_response(list(GAMES))

        game = GAMES.get(name)
        return json_response(game)

    async def post(self):
        try:
            game_config = await self.request.json()
        except JSONDecodeError as error:
            return json_response(str(error), status=404)
        game = GAMES.create(game_config['team'], game_config)
        return json_response(game, status=201)

    async def delete(self):
        name = self.request.match_info.get('name')
        GAMES.delete(name)
        return json_response({})

    async def put(self):
        name = self.request.match_info.get('name')
        game = GAMES.start(name)
        return json_response(game)


class AsteriosView(web.View):

    async def get(self):
        team = self.request.match_info.get('team')
        member = self.request.match_info.get('member')
        return json_response(GAMES.set_question(team, member))

    async def post(self):
        try:
            answer = await self.request.json()
        except JSONDecodeError as error:
            return json_response(str(error), status=404)

        team = self.request.match_info.get('team')
        member = self.request.match_info.get('member')

        is_exact, comment = GAMES.check_answer(team, member, answer)
        if is_exact:
            return json_response(comment, status=201)
        return json_response(comment, status=420)
