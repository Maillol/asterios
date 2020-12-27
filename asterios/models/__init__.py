from .basemodel import Collection
from .errors import GameConflict, GameDoesntExist, error_middleware
from .games import Game
from .team_members import TeamMember


class _GameCollection(Collection):
    """
    A collection of game

    The name of team is used as id of the game.
    """

    not_exist_error = GameDoesntExist

    def generate_id(self, obj):
        """
        This method gets the name of the team an return it.

        If the name is already used, returns a GameConflict exception.
        """
        id_ = obj.team
        if self.has_id(id_):
            raise GameConflict(
                "The game with name `{name}` already exists".format(name=id_)
            )
        return id_


class Model:
    """
    This class is a Facade providing method to manipulate the models.
    """

    def __init__(self):
        self._games = _GameCollection()

    def create(self, game):
        game = Game.from_dict(game)
        self._games.append(game)
        return game

    def game(self, name):
        """
        Return a game
        """
        game = self._games[name]
        game.set_remaining_time()
        return game

    def __iter__(self):
        for game in self._games:
            game.set_remaining_time()
            yield game

    def games(self):
        """
        Return all games
        """
        return list(self)

    def delete_game(self, name):
        """
        delete a game
        """
        self._games.delete(name)

    def start(self, name):
        """
        Stat a game
        """
        game = self.game(name)
        game.start()
        return game

    def drop(self):
        """
        Drop all games.
        """
        self._games.clear()

    def set_question(self, game_name, member_id):
        """
        Generate puzzle for `member_id` in the `game_name`.
        """
        self.game(game_name).ensure_state_is("started")
        member = self.member_from_id(game_name, member_id)
        return member.set_question()

    def check_answer(self, game_name, member_id, answer):
        """
        Check the `answer` for `member_id` in the `game_name`.
        """
        game = self.game(game_name)
        return game.check_answer(member_id, answer)

    def member_from_id(self, game_name, member_id):
        """
        Return a team member from an `id`.
        """
        game = self.game(game_name)
        return game.member_from_id(member_id)

    def member_from_name(self, game_name, member_name):
        """
        Return a team member from the member_name
        """
        game = self.game(game_name)
        return game.member_from_name(member_name)
