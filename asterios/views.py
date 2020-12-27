"""
This module contains the asterios view

A view is a class containing several HTTP handlers.
"""

from datetime import datetime
import json
from json.decoder import JSONDecodeError
from typing import Union, List

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r201, r404, r409, r420
from aiohttp_security import has_permission

from .level import LevelSet, Difficulty
from .models import TeamMember, Game
from .models.basemodel import Collection
from .schema import (
    ReturnedGameSchema,
    GameCreationSchema,
    ReturnedTeamMemberSchema,
    TeamMemberCreationSchema,
    ErrorSchema,
)


class JSONEncoder(json.JSONEncoder):
    """
    This JSONEncoder can encode datetime using ISO 8601 format
    and LevelSet object to dict with `theme` and `level` keys.
    """

    def default(self, o):
        """
        Encode Model object to JSON.
        """

        # pylint: disable=method-hidden, too-many-return-statements
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, LevelSet):
            return {"theme": o.theme, "level": o.level_number}
        if isinstance(o, Difficulty):
            return o.value
        if isinstance(o, TeamMember):
            return {
                "id": o.id,
                "name": o.name,
                "level": o.level,
                "level_max": o.level_max,
                "theme": o.theme,
                "difficulty": o.difficulty,
                "levels_obj": o.levels_obj,
                "won_at": o.won_at,
            }
        if isinstance(o, Collection):
            return list(o)
        if isinstance(o, Game):
            ret = {
                "team": o.team,
                "state": o.state,
                "duration": o.duration,
                "team_members": o.team_members,
            }

            if o.start_at is not None:
                ret["start_at"] = o.start_at

            if o.remaining is not None:
                ret["remaining"] = o.remaining

            return ret
        return json.JSONEncoder.default(self, o)


def json_response(obj, status=200):
    """
    Return a web.json_response manage model object json encoding.
    """
    return web.json_response(obj, status=status, dumps=JSONEncoder().encode)


class GameConfigCollectionView(PydanticView):
    """
    HTTP handlers to create a game or get all games.
    """

    async def get(self) -> r200[List[ReturnedGameSchema]]:
        """
        Return all created game.
        """
        result = self.request.app["model"].games()
        return json_response(result)

    async def post(
        self, game_config: GameCreationSchema
    ) -> Union[r201[ReturnedGameSchema], r409]:
        """
        Create a new game, The game will be identified by the name of
        the team. Each game has one uniq team. when the game is created,
        you should start it using PUT request on `/game-config/{team}/start` route

        Status Codes:
            201: The game is created.
        """
        game = self.request.app["model"].create(game_config.dict(exclude_unset=True))
        return json_response(game, status=201)


class GameConfigItemView(PydanticView):
    """
    HTTP handlers to get, delete, apply actions on a single game object.
    """

    async def get(
        self, name: str, /
    ) -> Union[r200[ReturnedGameSchema], r404[ErrorSchema]]:
        """
        Get a game from the team name.

        Status Codes:
            200: Return the game.
            404: The game is not found
        """
        result = self.request.app["model"].game(name)
        return json_response(result)

    @has_permission("gameconfig.delete")
    async def delete(self, name: str, /) -> Union[r200, r404[ErrorSchema]]:
        """
        Delete a created game.

        Status Codes:
            200: The game is deleted.
            404: The game is not found.
        """
        self.request.app["model"].delete_game(name)
        return json_response({})


class GameConfigActionStartView(PydanticView):
    async def put(
        self, name: str, /
    ) -> Union[r200[ReturnedGameSchema], r404[ErrorSchema], r409[ErrorSchema]]:
        """
        Start a created game configuration selected by `name`.

        Status Codes:
            200: The game is started
        """
        game = self.request.app["model"].game(name)
        game.start()
        return json_response(game)


class GameConfigActionAddMemberView(PydanticView):
    async def put(
        self, name: str, /, team_member: TeamMemberCreationSchema
    ) -> Union[r200[ReturnedGameSchema], r404[ErrorSchema], r409[ErrorSchema]]:
        """
        Add a new team member to a game. The state of game must be ready.

        Status Codes:
            200: The new member is added to the game.
            404: The game does not exist.
            409: The state of game do not allow to add a member.
        """
        game = self.request.app["model"].game(name)
        game.add_member(team_member.dict())
        return json_response(game)


class AsteriosItemView(PydanticView):
    async def get(
        self, team: str, team_member: str, /
    ) -> r200[ReturnedTeamMemberSchema]:
        """
        Return a member of team.
        """
        return json_response(
            self.request.app["model"].member_from_id(team, team_member)
        )


class AsteriosActionPuzzleView(PydanticView):
    """
    Define http handler to get puzzle and resolve it.
    """

    async def put(self, team: str, team_member: str, /) -> Union[r200, r404]:
        """
        Get puzzle of current level. A new puzzle is generated for each request

        Status Codes:
            200: A question is generated and returned.
            404: If the game or team member doesn't exist
        """
        return json_response(self.request.app["model"].set_question(team, team_member))


class AsteriosActionSolveView(PydanticView):
    """
    Define http handler to get puzzle and resolve it.
    """

    async def put(self, team: str, team_member: str, /) -> Union[r201, r404, r420]:
        """
        Try to solve the puzzle sending a response in the request body.

        Status Codes:
            201: The puzzle is solved.
            404: If the game or team member doesn't exist
            420: The puzzle isn't solved.
        """
        try:
            answer = await self.request.json()
        except JSONDecodeError as error:
            return json_response(str(error), status=400)

        is_exact, comment = self.request.app["model"].check_answer(
            team, team_member, answer
        )
        if is_exact:
            return json_response(comment, status=201)
        return json_response(comment, status=420)
